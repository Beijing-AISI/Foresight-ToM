python3 /mnt/home/liweiyi/LLM/json_results.py \
    --input_path /mnt/home/liweiyi/LLM/results/Qwen2.5-72B-Instruct/answers \
    --output_path /mnt/home/liweiyi/LLM/results/Qwen2.5-72B-Instruct/accuracy_results\

python3 /mnt/home/liweiyi/LLM/plot_results.py \
    --input_path /mnt/home/liweiyi/LLM/results/Qwen2.5-72B-Instruct/accuracy_results \
    --output_path /mnt/home/liweiyi/LLM/results/Qwen2.5-72B-Instruct/confusion_matrices \