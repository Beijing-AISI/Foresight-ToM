python3 /mnt/home/liweiyi/LLM/SimpleToM/generate_answers.py \
    --output_path "." \
    --output_folder "Llama-3.1-8B-Instruct" \
    --prompts_path ./prompts.py \
    --use_local \
    --local_model_path "/mnt/home/liweiyi/Model/meta-llama/Llama-3.1-8B-Instruct" \
    --try_times 5 \
    --seed 101 \
    --token_size 4096 \
    --device_map "cuda:3" \
