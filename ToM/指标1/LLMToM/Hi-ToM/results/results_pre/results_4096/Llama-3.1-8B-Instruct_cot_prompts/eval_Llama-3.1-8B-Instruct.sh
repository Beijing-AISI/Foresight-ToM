python3 /mnt/home/liweiyi/LLM/json_results.py \
    --input_path /mnt/home/liweiyi/LLM/results/results_pre/results_4096/Llama-3.1-8B-Instruct_cot_prompts/answers \
    --output_path /mnt/home/liweiyi/LLM/results/results_pre/results_4096/Llama-3.1-8B-Instruct_cot_prompts/accuracy_results\
    --prompt_type CoT MC \

python3 /mnt/home/liweiyi/LLM/plot_results.py \
    --input_path /mnt/home/liweiyi/LLM/results/results_pre/results_4096/Llama-3.1-8B-Instruct_cot_prompts/accuracy_results\
    --output_path /mnt/home/liweiyi/LLM/results/results_pre/results_4096/Llama-3.1-8B-Instruct_cot_prompts/confusion_matrices\
    --prompt_type CoT\
    --files_name joint
