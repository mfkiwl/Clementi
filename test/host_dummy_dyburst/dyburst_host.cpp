#include <cstdio>
#include <cstring>
#include <iostream>
#include <vector>
#include <algorithm>
#include <xcl2.hpp>

#include "rw_data_struct.h"

#include "pcg_basic.h"
#include "helper.h"




const char * free_run_kernel_list[] = {

};

cl::Kernel      krnl_free_run[ARRAY_SIZE(free_run_kernel_list)];

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <XCLBIN File>" << std::endl;
        return EXIT_FAILURE;
    }

    std::string binaryFile = argv[1];

    pcg32_srandom(42u, 54u);

    const size_t max_outdegree = 16;
    const size_t max_v = 1024 * 64 * 64 ;
    const size_t max_weight_value = 256;

    size_t max_e = SIZE_ALIGNMENT(max_v * max_outdegree, 16);

    std::vector<vertex_descriptor_t, aligned_allocator<vertex_descriptor_t> > vertex_desp_mem(max_v);
    std::vector<uint32_t, aligned_allocator<uint32_t> > adj(max_e);
    std::vector<uint32_t, aligned_allocator<uint32_t> > weight(max_e);


    std::vector<uint32_t, aligned_allocator<uint32_t> > res(max_e);

    uint32_t current_pos  = 0;
    for (size_t i = 0; i < max_v; i++) {
        vertex_descriptor_t v;
        v.start = current_pos;
#if 0
        if (i == 0)
            v.size  =  16 * 32;
        else

            v.size  =  pcg32_random() % max_outdegree;
#endif
        v.size = 16;



        for (size_t j = 0; j < v.size; j++)
        {
            adj[current_pos + j]   = j;
            weight[current_pos + j] = j;
        }
        current_pos += v.size;
        vertex_desp_mem[i] = v;


        res[i] = 0;
    }

    printf("size %d %ld\n", current_pos, max_e);


    cl_int err;
    cl::CommandQueue q;
    cl::CommandQueue free_run_q;
    cl::Context context;
    cl::Kernel      krnl_test_vertex_loader;
    cl::Kernel      krnl_single_burst;
    cl::Kernel      krnl_dynamic_burst_1;
    cl::Kernel      krnl_dynamic_burst_32;
    cl::Kernel      krnl_vd_scheduler;
    cl::Kernel      krnl_sampling;

    cl::Kernel      krnl_store;

    std::vector<cl::Device> devices = xcl::get_xil_devices();
    auto fileBuf = xcl::read_binary_file(binaryFile);
    cl::Program::Binaries bins{{fileBuf.data(), fileBuf.size()}};
    bool valid_device = false;
    for (unsigned int i = 0; i < devices.size(); i++) {
        auto device = devices[i];
        // Creating Context and Command Queue for selected Device
        OCL_CHECK(err, context = cl::Context(device, nullptr, nullptr, nullptr, &err));
        OCL_CHECK(err, q = cl::CommandQueue(context, device,
                                            CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE //| CL_QUEUE_PROFILING_ENABLE
                                            , &err));
        OCL_CHECK(err, free_run_q = cl::CommandQueue(context, device,
                                    CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE //| CL_QUEUE_PROFILING_ENABLE
                                    , &err));

        std::cout << "Trying to program device[" << i << "]: " << device.getInfo<CL_DEVICE_NAME>() << std::endl;
        cl::Program program(context, {device}, bins, nullptr, &err);
        if (err != CL_SUCCESS) {
            std::cout << "Failed to program device[" << i << "] with xclbin file!\n";
        } else {
            std::cout << "Device[" << i << "]: program successful!\n";

            for (unsigned int j = 0; j < ARRAY_SIZE(free_run_kernel_list); j++)
            {
                OCL_CHECK(err, krnl_free_run[j] = cl::Kernel(program, free_run_kernel_list[j], &err));
            }
            OCL_CHECK(err, krnl_single_burst = cl::Kernel(program, "single_burst:{single_burst_1}", &err));
            OCL_CHECK(err, krnl_dynamic_burst_1 = cl::Kernel(program, "dynamic_burst_1:{dynamic_burst_1_1}", &err));
            OCL_CHECK(err, krnl_dynamic_burst_32 = cl::Kernel(program, "dynamic_burst_32:{dynamic_burst_32_1}", &err));
            OCL_CHECK(err, krnl_vd_scheduler = cl::Kernel(program, "vd_scheduler:{vd_scheduler_1}", &err));
            //OCL_CHECK(err, krnl_sampling = cl::Kernel(program,  "dummy_sample:{dummy_sample_1}", &err));


            OCL_CHECK(err, krnl_test_vertex_loader = cl::Kernel(program, "test_vertex_loader:{test_vertex_loader_1}", &err));
            OCL_CHECK(err, krnl_store = cl::Kernel(program, "test_store_32:{test_store_32_1}", &err));

            valid_device = true;
            break; // we break because we found a valid device
        }
    }
    if (!valid_device) {
        std::cout << "Failed to program any device found, exit!\n";
        exit(EXIT_FAILURE);
    }

    OCL_CHECK(err, cl::Buffer buffer_vertex_desp(context,
              CL_MEM_USE_HOST_PTR,
              max_v * sizeof(vertex_descriptor_t), vertex_desp_mem.data(), &err));

    OCL_CHECK(err, cl::Buffer buffer_res(context,
                                         CL_MEM_USE_HOST_PTR,
                                         max_v * sizeof(uint32_t), res.data(), &err));

    OCL_CHECK(err, cl::Buffer buffer_weight(context,
                                            CL_MEM_USE_HOST_PTR,
                                            max_e * sizeof(uint32_t), weight.data(), &err))
    OCL_CHECK(err, cl::Buffer buffer_weight1(context,
              CL_MEM_USE_HOST_PTR,
              max_e * sizeof(uint32_t), weight.data(), &err))
    OCL_CHECK(err, cl::Buffer buffer_weight2(context,
              CL_MEM_USE_HOST_PTR,
              max_e * sizeof(uint32_t), weight.data(), &err))

    uint32_t number_of_query = max_v;
    uint32_t max_number_of_store = max_e;

    OCL_CHECK(err, err = q.enqueueMigrateMemObjects({   buffer_vertex_desp,
                                                    }, 0 /*0 means from host*/));

    OCL_CHECK(err, err = q.finish());

    for  (uint32_t burst_size = 1; burst_size < 64; burst_size +=1)
    {
        uint32_t mode = 16 * burst_size;

        OCL_CHECK(err, err = krnl_test_vertex_loader.setArg(0, number_of_query));

        OCL_CHECK(err, err = krnl_test_vertex_loader.setArg(1, buffer_vertex_desp));
        OCL_CHECK(err, err = krnl_test_vertex_loader.setArg(2, mode));

        OCL_CHECK(err, err = krnl_single_burst.setArg(0, buffer_weight));
        OCL_CHECK(err, err = krnl_dynamic_burst_1.setArg(0, buffer_weight1));
        OCL_CHECK(err, err = krnl_dynamic_burst_32.setArg(0, buffer_weight2));

        OCL_CHECK(err, err = krnl_store.setArg(0, max_number_of_store));

        OCL_CHECK(err, err = krnl_store.setArg(1, buffer_res));





        for (unsigned int j = 0; j < ARRAY_SIZE(free_run_kernel_list); j++)
        {
            OCL_CHECK(err, err = free_run_q.enqueueTask(krnl_free_run[j]));
        }


        std::vector<double> exec_time;
        for (int i = 0; i < 5; i ++)
        {
            double start, stop;
            start = getCurrentTimestamp();

            OCL_CHECK(err, err = q.enqueueTask(krnl_test_vertex_loader));
            OCL_CHECK(err, err = q.enqueueTask(krnl_single_burst));
            OCL_CHECK(err, err = q.enqueueTask(krnl_dynamic_burst_1));
            OCL_CHECK(err, err = q.enqueueTask(krnl_dynamic_burst_32));
            OCL_CHECK(err, err = q.enqueueTask(krnl_vd_scheduler));
            //OCL_CHECK(err, err = q.enqueueTask(krnl_sampling));

            OCL_CHECK(err, err = q.enqueueTask(krnl_store));
            stop = getCurrentTimestamp();
            printf("enqueue  time: %lf\n", stop - start);

            OCL_CHECK(err, err = q.finish());
            stop = getCurrentTimestamp();

            printf("burst_size %d exec time: %lf\n",burst_size, stop - start);
            exec_time.push_back(stop - start);
            OCL_CHECK(err, err = q.enqueueMigrateMemObjects({buffer_res}, CL_MIGRATE_MEM_OBJECT_HOST));
            OCL_CHECK(err, err = q.finish());
        }
        std::sort(exec_time.begin(), exec_time.end());
        printf("[MID] burst_size %d exec time: %lf\n",burst_size, exec_time[2]);

    }

    return 0;
}

