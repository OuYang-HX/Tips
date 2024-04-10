import pandas as pd

def find_missing_rows(file_202212, file_202306, output_file_202212_not_in_202306, output_file_202306_not_in_202212):
    # 读取Excel文件202212和202306
    df_202212 = pd.read_excel(file_202212)
    df_202306 = pd.read_excel(file_202306)

    # 查找202212中在202306中没有出现的行，并保存到表格"2022有202306没有"
    missing_rows_202212_not_in_202306 = df_202212[~df_202212.set_index(["规则", "文件路径"]).index.isin(df_202306.set_index(["规则", "文件路径"]).index)]
    missing_rows_202212_not_in_202306.to_excel(output_file_202212_not_in_202306, index=False)

    # 查找202306中在202212中没有出现的行，并保存到表格"2022没有202306有"
    missing_rows_202306_not_in_202212 = df_202306[~df_202306.set_index(["规则", "文件路径"]).index.isin(df_202212.set_index(["规则", "文件路径"]).index)]
    missing_rows_202306_not_in_202212.to_excel(output_file_202306_not_in_202212, index=False)

    print("已生成新的Excel文件，包含202212中在202306中没有出现的行、202306中在202212中没有出现的行。")

# 文件路径和输出文件名
file_202212 = "202212.xlsx"
file_202306 = "202306.xlsx"
output_file_202212_not_in_202306 = "2022有202306没有.xlsx"
output_file_202306_not_in_202212 = "2022没有202306有.xlsx"

# 调用函数
find_missing_rows(file_202212, file_202306, output_file_202212_not_in_202306, output_file_202306_not_in_202212)
