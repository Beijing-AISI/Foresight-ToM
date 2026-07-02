python3 /mnt/home/liweiyi/LLM/Hi-ToM/json_results.py \
    --input_path ./Llama-3.1-8B-Instruct/answers \
    --output_path ./Llama-3.1-8B-Instruct/accuracy_results\

# python3 /mnt/home/liweiyi/LLM/plot_results.py \
#     --input_path ./Llama-3.1-8B-Instruct/accuracy_results \
#     --output_path ./Llama-3.1-8B-Instruct/confusion_matrices\
#     --prompt_type CoT\
#     --files_name joint
