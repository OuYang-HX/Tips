from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import argparse

def read_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 去除每行末尾的换行符
    lines = [line.rstrip() for line in lines]

    return lines

def parse_markdown_to_excel(markdown_lines):
    wb = Workbook()
    ws = wb.active

    current_row = 1
    current_column = 1
    current_title = ''
    titles = {}

    in_code_block = False
    code_block_lines = []

    for line in markdown_lines:
        if line.startswith('# '):
            current_title = line.strip('# ').strip()
            current_row += 1
            current_column = 1
            ws.cell(row=current_row, column=current_column, value=current_title)
            titles[current_title] = current_row
        elif line.startswith('## '):
            sub_title = line.strip('## ').strip()
            current_column += 1
            ws.cell(row=1, column=current_column, value=sub_title)
        elif line.startswith('```'):
            if in_code_block:
                in_code_block = False
                code_content = '\n'.join(code_block_lines)
                ws.cell(row=titles[current_title], column=current_column, value=code_content)
                code_block_lines = []
            else:
                in_code_block = True
        else:
            if in_code_block:
                code_block_lines.append(line)
            else:
                if current_title in titles:
                    current_row = titles[current_title]
                    cell_value = ws.cell(row=current_row, column=current_column).value
                    if cell_value:
                        cell_value += "\n" + line
                    else:
                        cell_value = line
                    ws.cell(row=current_row, column=current_column, value=cell_value)
    
    # 设置单元格宽度
    # 设置单元格宽度为固定值
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = 20

    
    return wb

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Markdown to Excel')
    parser.add_argument('--input', type=str, help='Input Markdown file path', default='数据集.md')
    parser.add_argument('--output', type=str, help='Output Excel file path', default='数据集.xlsx')
    args = parser.parse_args()

    markdown_file = args.input
    excel_file = args.output

    markdown_lines = read_markdown_file(markdown_file)
    wb = parse_markdown_to_excel(markdown_lines)
    wb.save(excel_file)
    print(f"Excel file has been generated and saved to {excel_file}")
