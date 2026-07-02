python3 /mnt/home/liweiyi/LLM/json_results.py \
    --input_path /mnt/home/liweiyi/LLM/results/prompts/prompts3/Llama-3.1-8B-Instruct/answers \
    --output_path /mnt/home/liweiyi/LLM/results/prompts/prompts3/Llama-3.1-8B-Instruct/accuracy_results\
    --prompt_type CoT MC \

python3 /mnt/home/liweiyi/LLM/plot_results.py \
    --input_path /mnt/home/liweiyi/LLM/results/prompts/prompts3/Llama-3.1-8B-Instruct/accuracy_results \
    --output_path /mnt/home/liweiyi/LLM/results/prompts/prompts3/Llama-3.1-8B-Instruct/confusion_matrices\
    --prompt_type CoT\
    --files_name joint
