import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":
    # plt.figure(figsize=(6, 9))
    # data = {
    #     'raw': [100.00, 50.83, 27.50, 59.44],
    #     'ran_3': [93.33, 45.83, 19.17, 52.78],
    #     'ran_7': [90.83, 50.00, 21.67, 54.16],
    #     'story_3': [96.67, 49.16, 16.64, 54.44],
    #     'story_7': [91.67, 52.50, 19.16, 54.44]
    # }
    #
    # x_labels = ["Order1", "Order2", "Order3", "Total"]
    # x = range(len(x_labels))
    # colors = ['mediumseagreen', 'gold', 'darkorchid']
    #
    # plt.plot(x, data['raw'], label='Raw', color=colors[0])
    # plt.plot(x, data['ran_3'], label='RanTask3', color=colors[1], linestyle='--')
    # plt.plot(x, data['ran_7'], label='RanTask7', color=colors[1])
    # plt.plot(x, data['story_3'], label='StoryTask3', color=colors[2], linestyle='--')
    # plt.plot(x, data['story_7'], label='StoryTask7', color=colors[2])
    #
    # plt.xticks(x, x_labels)
    # plt.xlabel("Orders")
    # plt.ylabel("Accuracy (%)")
    #
    # plt.legend()
    # plt.title("Joint Accuracy on ToMChallenge")
    #
    # # for i in range(len(x_labels)):
    # #     # Normal Condition 数据点
    # #     plt.text(x[i], data_normal[i] + 4, f"{data_normal[i]:.2f}", ha='center', fontsize=10, color='darkgreen')
    # #     # Overload Condition 数据点
    # #     plt.text(x[i], data_overload[i] - 4, f"{data_overload[i]:.2f}", ha='center', fontsize=10, color='darkred')
    #
    # # plt.show()
    # plt.tight_layout()
    # plt.savefig("./plot2.png")
    # plt.show()
    data = pd.DataFrame({
        'Model': ['Llama-8B', 'Llama-8B', 'Llama-8B', 'Qwen-7B', 'Qwen-7B', 'Qwen-7B', 'Qwen-72B', 'Qwen-72B', 'Qwen-72B'],
        'TaskType': ['Raw', 'RanTask', 'StoryTask', 'Raw', 'RanTask', 'StoryTask', 'Raw', 'RanTask', 'StoryTask'],
        'Order1': [100.00, 93.33, 96.67, 90.83, 96.67, 99.16, 100.00, 100.00, 100.00],
        'Order2': [50.83, 45.83, 49.16, 50.00, 45.00, 50.83, 98.33, 68.33, 85.83],
        'Order3': [27.50, 19.17, 16.64, 50.00, 44.16, 44.16, 97.50, 54.16, 60.00],
        'Total': [59.44, 52.78, 54.16, 63.61, 61.94, 64.72, 98.61, 74.16, 81.94]
    })
    plt.figure(figsize=(16, 5))
    for i, model in enumerate(data.Model.unique()):
        print(model)
        d = data[data['Model'] == model]
        d_melted = d.melt(id_vars=['TaskType'], value_vars=['Order1', 'Order2', 'Order3', 'Total'],
                          var_name='Order', value_name='Score')
        print(d)
        print(d_melted)
        plt.subplot(1, 3, i + 1)
        sns.lineplot(x='Order', y='Score', hue='TaskType', style='TaskType', data=d_melted, legend='full', markers=True)
        plt.xlabel('Order', fontsize=12)
        plt.ylabel('Acc', fontsize=12)
        plt.legend(loc='lower left')
        plt.title(f'{model}', fontsize=14)
        plt.tight_layout()
    plt.savefig('./plot3.png')
    plt.show()

    #
    # # 设置绘图风格
    # sns.set(style="whitegrid")
    #
    # # 绘制折线图，每个模型分开，任务类型为不同的折线
    # plt.figure(figsize=(10, 6))
    # sns.lineplot(x='Order', y='Score', hue='TaskType', style='TaskType', markers=True,
    #              dashes=False, data=data_long, legend='full')
    #
    # # 设置标题和标签
    # plt.title('Scores of Different Models by Task Type', fontsize=14)
    # plt.xlabel('Order', fontsize=12)
    # plt.ylabel('Score', fontsize=12)
    # plt.legend(title='TaskType', loc='best')
    #
    # # 显示图形
    # plt.show()
