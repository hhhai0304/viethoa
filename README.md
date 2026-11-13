# Việt Hóa — bản dịch tiếng Việt cho game PC

Trang phát hành các bản Việt hóa do mình làm: patch cài tự động trên Windows và
Steam Deck / Linux, không cần BepInEx, không cần launch option.

**Website:** https://hhhai0304.github.io/viethoa/

## Bản Việt hóa hiện có

| Game | Nền tảng | Phiên bản | Cài bằng |
|---|---|---|---|
| [Temtem](https://hhhai0304.github.io/viethoa/temtem/) | PC (Windows, Steam Deck/Linux) | v1.0.0 | `install.bat` / `install.sh` |

## Cấu trúc repo

```
content/site.json          thông tin chung (domain, donate, tác giả)
content/games/<slug>.json  nội dung từng game — thêm game = thêm 1 file
static/                    style.css, app.js, ảnh
build.py                   render HTML + sitemap + robots (Python stdlib)
```

Chạy lại sau khi sửa nội dung:

```bash
python3 build.py
```

## Nguyên tắc

- Bản dịch miễn phí, không bán, không kèm file game gốc.
- Gói cài chỉ chứa phần chữ đã dịch + script cài; bạn cần sở hữu game trên Steam.
- Tên riêng (tên nhân vật, chiêu thức, vật phẩm, địa danh) giữ nguyên tiếng Anh.
- Mỗi bản phát hành có chữ ký `Việt hóa bởi viethoa.haiho.net` trong game.

## Gỡ cài

Steam → chuột phải game → Properties → Installed Files → **Verify integrity of
game files**. Không cần công cụ.

## Bản quyền

Phần dịch thuật thuộc về tác giả. Game và tài nguyên gốc thuộc về nhà phát hành;
vui lòng mua game để ủng hộ họ.
