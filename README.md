# VzCore

VzCore là một phiên bản phát triển từ cấu trúc trong `Vz_sign.zip`: một runtime nhỏ cho ngôn ngữ `.vz`, có parser → compiler → bytecode → runtime → system CLI.

## Mục tiêu

- Giữ cú pháp Vz đơn giản.
- Chạy tốt trên điện thoại/Termux/Pydroid.
- Tách parser, compiler, runtime và dữ liệu.
- Có permission cơ bản.
- Có command block.
- Có `show`, `set`, `print`, `require`.
- Có kiểm tra lỗi theo số dòng.
- Không phụ thuộc thư viện ngoài Python.

## Cấu trúc

```text
.
├── main.py
├── System
├── data/
│   └── config.vzdata
├── examples/
│   ├── system.vz
│   └── overview.vz
├── tests/
│   └── test_engine.py
└── vzcore/
    ├── __init__.py
    ├── parser.py
    ├── compiler.py
    ├── runtime.py
    └── system.py
```

## Chạy

```bash
python main.py
```

Sau đó:

```text
Vz> help
Vz> info
Vz> overview
Vz> show nation.name
Vz> run overview
Vz> set nation.population = 500000000
Vz> show nation.population
Vz> reload
Vz> exit
```

## Cú pháp Vz

```vz
system "Vinh Quang Vz"

set nation.name = "Đế chế Vzcomm"
set nation.population = 436000000

command "overview" {
    print "======= NATIONAL OVERVIEW ======="
    show nation.name
    show nation.population
}
```

Biến có thể tham chiếu bằng dấu `$`:

```vz
set greeting = "Xin chào"
print $greeting
```

Permission:

```vz
require overview.read
```

Các permission trong file `System` được nạp khi khởi động. `admin.*` có quyền vượt qua mọi permission.

## Nguồn tham khảo

Thiết kế của dự án này lấy cảm hứng trực tiếp từ cấu trúc trong file `Vz_sign.zip` do chủ repo cung cấp: các file `parser.py`, `compiler.py`, `runtime.py`, `system.py`, cú pháp `.vz`, `config.vzdata` và hệ thống permission.

Đây là một implementation mới, không phải bản sao nguyên trạng.
