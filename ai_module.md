# 大模型推理优化 3天天才速成｜全套可直连资源
## 适配方向：CUDA底层 / LLM推理 / SG静态调度 / SGLang / NanoVM 轻量虚拟机

## 一、CUDA 底层 + 高性能算子（Day1 核心必学）
### 官方文档
- [NVIDIA CUDA 官方文档(英文权威)](https://docs.nvidia.com/cuda/)
- [NVIDIA 中国区 CUDA 中文文档](https://developer.nvidia.cn/cuda)

### 核心源码仓库
- [NVIDIA CUTLASS 官方高性能GEMM算子库](https://github.com/NVIDIA/cutlass)
- [FlashAttention2 / FlashAttention3 原版仓库](https://github.com/Dao-AILab/flash-attention)
- [FlashInfer SGLang 底层高性能算子库](https://github.com/flashinfer-ai/flashinfer)
- [CUDA-LLM 极简算子示例：矩阵乘/ROPE/SOFTMAX](https://github.com/llm-learning/cuda-samples-llm)

## 二、工业级推理框架｜PagedAttention 连续批推理
- [vLLM 主仓库(PagedAttention 发源地)](https://github.com/vllm-project/vllm)
- [PagedAttention 原始论文](https://arxiv.org/abs/2309.06180)
- [vLLM 中文源码解析笔记](https://github.com/zhihu/vllm-cn)
- [llama.cpp 纯C++轻量推理/类NanoVM架构](https://github.com/ggerganov/llama.cpp)
- [llama.cpp 国内GitCode镜像](https://gitcode.com/zz/llama.cpp)

## 三、SG静态调度 · SGLang 专项核心
- [SGLang 官方仓库(SG-Lang 静态调度)](https://github.com/sgl-project/sglang)
- [SGLang 国内GitCode镜像](https://gitcode.com/GitHub_Trending/sg/sglang)
- [SGLang 官方完整文档](https://docs.sglang.ai/)
- [SGLang 静态调度原论文](https://arxiv.org/abs/2410.23768)
- [SGLang 调度器核心源码目录](https://github.com/sgl-project/sglang/tree/main/sglang/scheduler)

## 四、NanoVM 轻量推理虚拟机 全套
- [nanoLLM 官方 端侧NanoVM轻量化推理](https://github.com/mit-han-lab/nanoLLM)
- [nanoLLM NanoVM 核心源码目录](https://github.com/mit-han-lab/nanoLLM/tree/main/nanovm)
- [tinygrad 极简IR+指令集VM 参考架构](https://github.com/tinygrad/tinygrad)
- [TVM 工业级深度学习VM/IR编译器](https://github.com/apache/tvm)

## 五、量化推理源码｜INT4/INT8/FP8/AWQ/GPTQ
- [AWQ 量化算法官方实现](https://github.com/mit-han-lab/llm-awq)
- [GPTQ 大模型量化社区实现](https://github.com/oobabooga/GPTQ-for-LLaMa)
- [TensorRT-LLM 英伟达官方推理/FP8优化](https://github.com/NVIDIA/TensorRT-LLM)

## 六、3天可直接运行｜极简Demo工程
- [CUDA-LLM 从零手写算子完整Demo](https://github.com/llm-learning/cuda-llm-demo)
- [vLLM PagedAttention 核心源码文件](https://github.com/vllm-project/vllm/blob/main/vllm/attention/paged_attention.py)
- [NanoVM 最小可运行测试示例](https://github.com/mit-han-lab/nanoLLM/tree/main/examples)
- [llm.c 纯C/CUDA 极简大模型手搓项目](https://github.com/karpathy/llm.c)

## 七、必读核心论文（速成只看摘要+架构图）
- [FlashAttention2 论文](https://arxiv.org/abs/2307.08691)
- [FlashAttention3 论文](https://arxiv.org/abs/2407.08691)
- [大模型高效推理 中文高质量综述](https://arxiv.org/abs/2504.19720)

## 八、C++/CUDA 工程编译参考
- [CMake CUDA 混合编程模板](https://github.com/ptillet/triton/blob/master/CMakeLists.txt)
