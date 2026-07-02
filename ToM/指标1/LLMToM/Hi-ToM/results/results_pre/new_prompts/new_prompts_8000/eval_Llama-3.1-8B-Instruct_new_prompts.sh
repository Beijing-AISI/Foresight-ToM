python3 /mnt/home/liweiyi/LLM/json_results.py \
    --input_path /mnt/home/liweiyi/LLM/results/new_prompts_8000/Llama-3.1-8B-Instruct_new_prompts/answers \
    --output_path /mnt/home/liweiyi/LLM/results/new_prompts_8000/Llama-3.1-8B-Instruct_new_prompts/accuracy_results\
    --prompt_type CoT MC \

python3 /mnt/home/liweiyi/LLM/plot_results.py \
    --input_path /mnt/home/liweiyi/LLM/results/new_prompts_8000/Llama-3.1-8B-Instruct_new_prompts/accuracy_results \
    --output_path /mnt/home/liweiyi/LLM/results/new_prompts_8000/Llama-3.1-8B-Instruct_new_prompts/confusion_matrices\
    --prompt_type CoT\
    --files_name joint
