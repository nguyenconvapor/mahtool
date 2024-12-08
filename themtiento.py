def add_prefix_to_file(file_name, prefix):
  """Thêm tiền tố vào mỗi dòng trong file .txt

  Args:
    file_name: Tên file .txt cần sửa
    prefix: Tiền tố muốn thêm
  """

  try:
    with open(file_name, 'r') as f:
      lines = f.readlines()

    new_file_name = f"{file_name}_{prefix}.txt"
    with open(new_file_name, 'w') as f:
      for line in lines:
        f.write(prefix + line)

    print(f"Đã thêm tiền tố '{prefix}' vào file '{file_name}' và tạo file mới '{new_file_name}'")
  except FileNotFoundError:
    print(f"Không tìm thấy file '{file_name}'")

if __name__ == "__main__":
  file_name = input("Nhập tên file .txt: ")
  prefix = input("Nhập tiền tố muốn thêm: ")

  add_prefix_to_file(file_name, prefix)