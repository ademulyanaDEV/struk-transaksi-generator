import json  # Pastikan modul json diimpor
import requests
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
import io
import os

# Fungsi untuk mengunduh font dari URL
def download_font(url, font_path):
    response = requests.get(url)
    with open(font_path, 'wb') as f:
        f.write(response.content)
    print(f"Font berhasil diunduh dan disimpan di {font_path}")

# Fungsi untuk menghasilkan gambar struk
def generate_receipt(data, output_filename, font_path):
    # Mengatur dimensi gambar
    width = 400
    height = 600 + len(data['items']) * 30  # Tinggi gambar menyesuaikan jumlah item
    receipt = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(receipt)

    # Memuat font dari path lokal
    try:
        font = ImageFont.truetype(font_path, 20)  # Menggunakan font online yang sudah diunduh
    except IOError:
        font = ImageFont.load_default()

    # Header Struk
    draw.text((10, 10), data['store_name'], font=font, fill='black')
    draw.text((10, 30), data['store_address'], font=font, fill='black')
    draw.text((10, 50), f"Tel: {data['store_contact']}", font=font, fill='black')
    draw.text((10, 70), f"Date: {data['date']}    Time: {data['time']}", font=font, fill='black')

    # Nomor Transaksi
    draw.text((10, 90), f"Transaction: {data['transaction_number']}", font=font, fill='black')

    # Detail Barang yang Dibeli
    y_position = 110
    for item in data['items']:
        draw.text((10, y_position), f"{item['name']}  x{item['quantity']}  @ {item['price']}", font=font, fill='black')
        y_position += 30

    # Footer Struk
    draw.text((10, y_position + 20), f"Subtotal: {data['subtotal']}", font=font, fill='black')
    draw.text((10, y_position + 40), f"Discount: {data['discount']}", font=font, fill='black')
    draw.text((10, y_position + 60), f"Total: {data['total']}", font=font, fill='black')
    draw.text((10, y_position + 80), f"Payment Method: {data['payment_method']}", font=font, fill='black')
    draw.text((10, y_position + 100), f"Change: {data['change']}", font=font, fill='black')

    # Generate Barcode dari Nomor Transaksi
    barcode_class = barcode.get_barcode_class('code128')
    barcode_data = barcode_class(data['transaction_number'], writer=ImageWriter())
    
    # Menyimpan barcode ke dalam objek in-memory
    barcode_buffer = io.BytesIO()
    barcode_data.write(barcode_buffer)
    barcode_image = Image.open(barcode_buffer)

    # Tempelkan barcode pada gambar struk
    receipt.paste(barcode_image, (10, y_position + 120))

    # Simpan gambar struk
    receipt.save(output_filename)
    print(f"Struk berhasil dibuat dengan nama '{output_filename}'.")

# Fungsi untuk membaca data dari file JSON
def load_data_from_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Main program
if __name__ == "__main__":
    # URL font (contoh menggunakan font Roboto dari Google Fonts)
    font_url = "https://github.com/google/fonts/blob/main/apache/roboto/Roboto-Regular.ttf?raw=true"
    font_path = "Roboto-Regular.ttf"

    # Unduh font jika belum ada
    if not os.path.exists(font_path):
        download_font(font_url, font_path)

    # Membuat folder transaksi jika belum ada
    folder_path = "pngtransaksi"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' berhasil dibuat.")

    # Membaca data dari data.json
    transactions = load_data_from_json('data.json')

    # Menghasilkan gambar struk untuk setiap transaksi
    for i, transaction in enumerate(transactions, start=1):
        output_filename = os.path.join(folder_path, f'receipt_{transaction["transaction_number"]}.png')
        generate_receipt(transaction, output_filename, font_path)
