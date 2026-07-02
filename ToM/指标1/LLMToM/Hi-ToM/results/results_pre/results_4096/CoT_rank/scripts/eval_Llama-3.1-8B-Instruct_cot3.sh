# python3 /mnt/home/liweiyi/LLM/json_results.py \
#     --input_path /mnt/home/liweiyi/LLM/results/CoT_rank/Llama-3.1-8B-Instruct_cot3/answers \
#     --output_path /mnt/home/liweiyi/LLM/results/CoT_rank/Llama-3.1-8B-Instruct_cot3/accuracy_results\
#     --prompt_type CoT MC \

python3 /mnt/home/liweiyi/LLM/plot_results.py \
    --input_path /mnt/home/liweiyi/LLM/results/CoT_rank/Llama-3.1-8B-Instruct_cot3/accuracy_results \
    --output_path /mnt/home/liweiyi/LLM/results/CoT_rank/Llama-3.1-8B-Instruct_cot3/confusion_matrices\
    --prompt_type CoT\
    --files_name joint 
