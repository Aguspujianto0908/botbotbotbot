import json
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode  # Perubahan impor ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes, ConversationHandler
from telegram import Bot
import random
import hashlib
import asyncio
import threading


# Langkah percakapan
NAME, AGE, GENDER, NOTE, ISLAND, PROVINCE, CITY, PHOTO = range(8)

# Peta pulau dan provinsi
island_province_map = {
    "Sumatra": ["Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Kepulauan Riau", "Jambi", "Bengkulu", "Sumatera Selatan", "Kepulauan Bangka Belitung", "Lampung"],
    "Jawa": ["DKI Jakarta", "Jawa Barat", "Jawa Tengah", "Jawa Timur", "Banten", "Yogyakarta"],
    "Kalimantan": ["Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Timur", "Kalimantan Selatan", "Kalimantan Utara"],
    "Sulawesi": ["Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Selatan", "Sulawesi Tenggara", "Gorontalo", "Sulawesi Barat"],
    "Bali": ["Bali"],
    "Nusa Tenggara": ["Nusa Tenggara Barat", "Nusa Tenggara Timur"],
    "Maluku": ["Maluku", "Maluku Utara"],
    "Papua": ["Papua", "Papua Barat", "Papua Tengah", "Papua Pegunungan", "Papua Selatan", "Papua Barat Daya"]
}


# Fungsi untuk memuat data data_diri user dari file JSON
def load_user_data():
    try:
        with open("userdata.json", 'r') as file:
            content = file.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error membaca file JSON: {e}")
        return {}
    
def save_user_data(user_id, user_data):
    # Memuat data pengguna yang ada
    existing_data = load_user_data()

    # Memperbarui data pengguna dengan ID yang sama
    existing_data[user_id] = user_data

    # Menyimpan kembali data pengguna yang telah diperbarui
    with open("userdata.json", 'w') as file:
        json.dump(existing_data, file, indent=4)
        
# //////////////////////////////////////////////////////////////////////////////////////////////////////////
def load_like_data_user():
    # Cek apakah file ada dan tidak kosong
    if not os.path.exists('like_data_user.json'):

        return []  # Kembalikan list kosong jika file tidak ada atau kosong
    
    try:
        with open('like_data_user.json', 'r', encoding='utf-8') as file:
            data = json.load(file)  # Muat data JSON
            return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []  # Kembalikan list kosong jika terjadi error dalam memuat JSON
    except Exception as e:
        print(f"Error loading file: {e}")
        return []  # Jika terjadi error lainnya, kembalikan list kosong
    
def save_data_like_user(likes_data):
    try:
        with open('like_data_user.json', 'w', encoding='utf-8') as file:
            json.dump(likes_data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving data: {e}")
        

def tambah_data_like_user(viewer_user_id, selected_user_id, viewer_username, selected_user_username):
    # Memastikan ID disimpan dalam bentuk string
    viewer_user_id = str(viewer_user_id)
    selected_user_id = str(selected_user_id)
    
    likes_data = load_like_data_user()  # Memuat data like yang ada

    # Data baru yang ingin ditambahkan
    new_like_data = {
        "viewer_user_id": viewer_user_id,
        "viewer_username": viewer_username,
        "selected_user_id": selected_user_id,
        "selected_user_username": selected_user_username
    }
    
    # Jika data belum ada, tambahkan data baru
    likes_data.append(new_like_data)
    save_data_like_user(likes_data)  # Simpan data yang baru ditambahkan


# Fungsi untuk mengambil username berdasarkan user_id
def get_username_by_user_id(user_id):
    """Function to get the username of a user based on their user ID."""
    user_data = load_user_data()  # Pastikan load_user_data() tersedia dan benar
    
    # Periksa apakah user_id ada di dalam data pengguna
    if str(user_id) in user_data:
        # Mengambil username jika ada
        return user_data[str(user_id)].get('username', 'No username available')
    return None

def count_likes_for_user(user_id: str) -> int:
    try:
        # Membaca data dari file JSON
        with open('like_data_user.json', 'r') as file:
            data = json.load(file)

        # Menghitung jumlah likes untuk user_id tertentu
        like_count = sum(1 for like in data if like["selected_user_id"] == user_id)
        return like_count

    except FileNotFoundError:
        print("File like_data_user.json tidak ditemukan.")
        return 0
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return 0
    
    
# //////////////////////////////////////////////////////////////////////////////////////////////////////////

# Fungsi untuk menangani /start
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    username = user.username
    keyboard = [
        ["Lihat Profil Orang", "Profil"]
    ]
    tombol_menu = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    # Cek jika pengguna memiliki username
    if not username:
        # Jika tidak ada username, beri tahu pengguna dan hentikan eksekusi lebih lanjut
        await update.message.reply_text("Kamu harus memiliki username untuk menggunakan bot ini!")
        return  # Menghentikan eksekusi lebih lanjut

    # Jika pengguna memiliki username, lanjutkan dengan pesan selamat datang
    if username:
        await update.message.reply_text(text="Bot ini masih dalam tahap pengembangan, di tunggu update selanjutnya berikan feedback atau fitur apa yang ingin kalian inginkan di bot ini ke team kami @tomi9851", reply_markup=tombol_menu)
    
    # Menangani pesan selain perintah '/start'
    else:
        await None

    
async def profile(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)  # Mengambil ID pengguna
    user_data = load_user_data()  # Memuat data pengguna dari file JSON
    keyboard = [
        ["Edit Profil"],
        ["Menu"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    # Jika data pengguna ditemukan
    if user_id in user_data:
        profile = user_data[user_id]
        
        # Menyusun pesan teks yang akan digabungkan dengan caption foto
        message = f"{profile.get('name')}, {profile.get('age')}, {profile.get('gender')}, {profile.get('province')}, {profile.get('city')}"
        
        # Menambahkan catatan jika ada dan bukan "Tidak ada catatan."
        if 'note' in profile and profile['note'] and profile['note'] != "Tidak ada catatan.":
            message += f", {profile['note']}"

        # Menyediakan foto jika ada
        if 'photo' in profile:
            photo_path = profile['photo']
            try:
                # Mengirimkan foto dengan caption yang berisi data profil pengguna
                with open(photo_path, 'rb') as photo_file:
                    await update.message.reply_photo(photo=photo_file, caption=message, reply_markup=reply_markup)
            except FileNotFoundError:
                # Jika foto tidak ditemukan, kirimkan pesan teks saja
                message += "\nFoto tidak ditemukan."
                await update.message.reply_text(message, reply_markup=reply_markup)
        
    else:
        # Jika data pengguna belum ada, kirimkan pesan untuk mengisi data
        message = "Kamu belum mengisi identitas, silakan isi terlebih dahulu."
        keyboard = [
            ["Edit Profil"],
            ["Menu"]
        ]
        tombol_menu = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=tombol_menu)
        return  # Tidak lanjutkan proses jika belum ada data 
    # Menangani tombol "Kembali"

async def menu(update: Update, context: CallbackContext):
    await start_bot_1(update, context)

async def start_edit_profile(update: Update, context: CallbackContext):
    # Mulai percakapan dari langkah NAME
    user_id = update.message.from_user.id
    context.user_data['step'] = NAME  # Menandakan percakapan dimulai dengan langkah NAME
    await update.message.reply_text("Silakan masukkan nama Anda.")
    return NAME  # Kembali ke percakapan setelah langkah pertama

async def ask_name(update: Update, context: CallbackContext):
    user_data = context.user_data
    user_data['name'] = update.message.text  # Menyimpan nama
    user_data['step'] = AGE  # Pindah ke langkah berikutnya (AGE)
    await update.message.reply_text("Berapa umur Anda?")
    return AGE  # Pindah ke langkah AGE

async def ask_age(update: Update, context: CallbackContext):
    user_data = context.user_data
    try:
        # Mencoba mengonversi input menjadi integer
        user_data['age'] = int(update.message.text)  # Menyimpan umur
        user_data['step'] = GENDER  # Pindah ke langkah berikutnya (gender)
        
        # Menyiapkan keyboard untuk memilih gender
        keyboard = [['cowok', 'cewek']]
        tombol_gender = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text("Apa jenis kelamin kamu?", reply_markup=tombol_gender)
        return GENDER  # Pindah ke langkah GENDER
    
    except ValueError:
        # Jika input tidak valid, beri tahu pengguna
        await update.message.reply_text("Mohon masukkan umur dengan angka yang valid.")
        return AGE  # Tetap di langkah AGE untuk meminta ulang umur

async def ask_gender(update: Update, context: CallbackContext):
    user_data = context.user_data
    user_data['gender'] = update.message.text  # Menyimpan gender
    user_data['step'] = NOTE  # Pindah ke langkah island
    keyboard = [['Lewati']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Ceritakan tentang dirimu...", reply_markup=reply_markup)
    return NOTE  # Pindah ke langkah note

async def ask_note(update: Update, context: CallbackContext):
    user_data = context.user_data
    
    # Cek apakah pengguna mengirimkan "Lewati"
    if update.message.text == "Lewati":
        user_data['note'] = "Tidak ada catatan."  # Atau Anda bisa menyimpan nilai lain sesuai kebutuhan
        user_data['step'] = ISLAND  # Pindah ke langkah ISLAND
        
        # Menyiapkan keyboard untuk memilih pulau
        keyboard = [
            ["Sumatra", "Jawa", "Kalimantan"],
            ["Sulawesi", "Bali", "Nusa Tenggara"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text("Dimana tempat tinggal kamu?", reply_markup=reply_markup)
        return ISLAND  # Pindah ke langkah ISLAND
    
    # Jika pengguna memasukkan catatan
    user_data['note'] = update.message.text  # Menyimpan catatan
    user_data['step'] = ISLAND  # Pindah ke langkah ISLAND
    
    # Menyiapkan keyboard untuk memilih pulau
    keyboard = [
        ["Sumatra", "Jawa", "Kalimantan"],
        ["Sulawesi", "Bali", "Nusa Tenggara"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text("Dimana tempat tinggal kamu?", reply_markup=reply_markup)
    return ISLAND  # Pindah ke langkah ISLAND


async def ask_pulau(update: Update, context: CallbackContext):
    user_data = context.user_data
    user_data['island'] = update.message.text  # Menyimpan lokasi pulau
    user_data['step'] = PROVINCE  # Pindah ke langkah berikutnya (PROVINCE)
    
    # Menyiapkan keyboard untuk memilih provinsi
    provinces = island_province_map.get(user_data['island'], [])
    
    # Membagi provinsi menjadi 3 baris
    keyboard = []
    for i in range(0, len(provinces), 3):
        keyboard.append(provinces[i:i + 3])  # Menambahkan provinsi dalam grup 3

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text("Pilih provinsi Anda:", reply_markup=reply_markup)
    return PROVINCE  # Pindah ke langkah PROVINCE

async def ask_provinsi(update: Update, context: CallbackContext):
    user_data = context.user_data 
    user_data['province'] = update.message.text  # Menyimpan lokasi provinsi
    user_data['step'] = CITY  # Pindah ke langkah berikutnya (CITY)
    await update.message.reply_text("Masukan kota tempat anda tinggal sekarang.")
    return CITY  # Pindah ke langkah CITY

async def ask_kota(update: Update, context: CallbackContext):
    user_data = context.user_data
    user_data['city'] = update.message.text  # Menyimpan lokasi kota
    user_data['step'] = PHOTO  # Pindah ke langkah berikutnya (PHOTO)
    await update.message.reply_text("Kirimkan foto yang ingin Anda gunakan sebagai profil.")
    return PHOTO  # Pindah ke langkah PHOTO

async def save_photo(update: Update, context: CallbackContext):
    user_data = context.user_data

    try:
        # Memeriksa apakah pesan berisi foto
        if update.message.photo:
            # Mengambil file foto dengan ukuran terbesar
            photo_file = await update.message.photo[-1].get_file()
            photo_path = f"photos/{update.message.from_user.id}_photo.jpg"

            # Pastikan folder photos ada, jika tidak buat folder tersebut
            if not os.path.exists('photos'):
                os.makedirs('photos')

            # Mengunduh file foto ke direktori lokal
            await photo_file.download_to_drive(photo_path)

            # Menyimpan path foto dalam user_data
            user_data['photo'] = photo_path  

            # Menyimpan username dalam user_data secara otomatis
            username = update.message.from_user.username
            user_data['username'] = username if username else 'NoUsername'  # Cek apakah username ada

            # Menyimpan data pengguna setelah foto diunduh
            user_id = str(update.message.from_user.id)  # Pastikan ID adalah string
            save_user_data(user_id, user_data)  # Memperbarui data pengguna

            keyboard = ReplyKeyboardMarkup([["Menu"]], one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("Profil Anda telah diperbarui!", reply_markup=keyboard)
            del user_data['step']  # Menghapus step agar percakapan selesai
            return ConversationHandler.END  # Mengakhiri percakapan
        
        else:
            await update.message.reply_text("Mohon kirimkan foto.")
            return PHOTO  # Jika tidak ada foto, kembali ke langkah PHOTO
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        await update.message.reply_text("Terjadi kesalahan saat menyimpan foto. Silakan coba lagi.")
        return PHOTO  # Kembali ke langkah PHOTO jika terjadi error
    
async def Lihat_Profil_Orang(update: Update, context: CallbackContext) -> None:
    user_data = load_user_data()  
    user_id = str(update.message.from_user.id)
    

    # Memuat data dari file
    likes_data = load_like_data_user()
    room_data = await load_data_room_user()

    # Mendapatkan jenis kelamin pengguna saat ini
    user_gender = user_data[user_id].get('gender')

    # Menyaring profil yang belum disukai
    liked_profiles = {like['selected_user_id'] for like in likes_data if like['viewer_user_id'] == user_id}

    # Menyaring profil berdasarkan room_data
    # Mengambil user_id dari room_data
    room_user_ids = {room['selected_user_id'] for room in room_data}

    # Menyaring profil yang tersedia
    available_profiles = {
    uid: data for uid, data in user_data.items() 
    if uid != user_id 
    and uid not in liked_profiles 
    and data.get('gender') != user_gender  # Filter lawan jenis
    and uid not in room_user_ids  # Menyaring berdasarkan room_data
    }

    if not available_profiles:
        await update.message.reply_text("Tidak ada profil lain yang tersedia untuk dilihat.")
        return
    

    selected_user_id, selected_user_data = random.choice(list(available_profiles.items()))


    name = selected_user_data['name']
    age = selected_user_data['age']
    gender = selected_user_data['gender']
    city = selected_user_data['city']
    province = selected_user_data['province']
    photo = selected_user_data['photo']

 
    profile_message = f"{name}, {age}, {gender}, {province}, {city}"

    if 'note' in selected_user_data and selected_user_data['note'] and selected_user_data['note'] != 'Tidak ada catatan.':
        profile_message += f", {selected_user_data['note']}\n\n"

    keyboar = [
        ["👌", "🗣", "😪"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboar, one_time_keyboard=True, resize_keyboard=True)
    

    if photo:
        try:
            with open(photo, 'rb') as photo_file:
                await update.message.reply_photo(photo=photo_file, caption=profile_message, reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text(f"Error dalam mengirim foto: {str(e)}")
    else:
        await update.message.reply_text(profile_message)
    context.user_data['selected_user_id'] = selected_user_id
    context.user_data['viewer_user_id'] = user_id
    

    
async def like(update: Update, context: CallbackContext):

    viewer_user_id = update.message.from_user.id  # ID pengguna yang memberi like (viewer)
    viewer_username = update.message.from_user.username  # Username pengguna yang memberi like
    
    # Mendapatkan ID pengguna yang disukai dari context
    selected_user_id = context.user_data.get('selected_user_id')

    await Lihat_Profil_Orang(update, context)
    
    if selected_user_id:
        # Ambil username pengguna yang disukai
        selected_user_username = get_username_by_user_id(selected_user_id)
        
        if selected_user_username:
            # Memperbarui atau menambahkan data like ke file JSON
            tambah_data_like_user(viewer_user_id, selected_user_id, viewer_username, selected_user_username)
            
            # Hitung jumlah orang yang menyukai pengguna yang dipilih
            like_count = count_likes_for_user(selected_user_id)  # Fungsi untuk menghitung jumlah likes
            
            # Kirimkan pesan ke pemilik profil yang disukai (Pengguna 2)
            message = f"Kamu disukai oleh {like_count} orang, tampilkan dia?"

            keyboard = [
                ["Coba Lihat 🔥"]
            ]
            pesan = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await context.bot.send_message(chat_id=selected_user_id, text=message, reply_markup=pesan)
        else:
            await update.message.reply_text("Pengguna yang disukai tidak memiliki username.")
    else:
        None



        
def count_room_for_user(user_id: str) -> int:
    try:
        # Membaca data dari file JSON
        with open('rooms_data_user.json', 'r') as file:
            data = json.load(file)

        # Menghitung jumlah likes untuk user_id tertentu
        like_count = sum(1 for like in data if like["selected_user_id"] == user_id)
        return like_count

    except FileNotFoundError:
        print("File rooms_data_user.json tidak ditemukan.")
        return 0
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return 0
    
# Fungsi untuk menampilkan data like
async def Coba_Liat_Like(update: Update, context: CallbackContext):
    # Periksa apakah pesan yang diterima adalah "Coba Lihat 🔥"
    if update.message.text != "Coba Lihat 🔥":
        return  # Hentikan eksekusi fungsi jika teks tidak sesuai

    # ID pengguna yang memiliki profil (profile_user_id)
    profile_user_id = update.message.from_user.id

    # Memuat data like dari file JSON
    likes_data = load_like_data_user()

    # Mencari data like untuk profile_user_id dalam list likes_data
    for like_info in likes_data:
        # Mengonversi selected_user_id menjadi integer untuk perbandingan
        selected_user_id = int(like_info["selected_user_id"])

        # Cek apakah selected_user_id dalam like_info adalah profile_user_id
        if selected_user_id == profile_user_id:
            viewer_user_id = like_info["viewer_user_id"]

            # Mendapatkan informasi profil pengguna yang memberi like
            try:
                # Mengambil data diri pengguna yang memberi like dari userdata.json
                user_data = load_user_data()

                # Pastikan data pengguna ada dalam file
                if str(viewer_user_id) in user_data:  # Mengonversi viewer_user_id menjadi string jika diperlukan
                    viewer_info = user_data[str(viewer_user_id)]  # Mengambil data pengguna berdasarkan ID yang tepat
                    viewer_full_name = viewer_info.get("name")
                    viewer_age = viewer_info.get("age")
                    viewer_gender = viewer_info.get("gender")
                    viewer_province = viewer_info.get("province")
                    viewer_city = viewer_info.get("city")
                    viewer_photo = viewer_info.get("photo", None)  # Bisa berupa path foto jika ada

                profile_message = f"{viewer_full_name}, {viewer_age}, {viewer_gender}, {viewer_province}, {viewer_city}"

                if 'note' in viewer_info and viewer_info["note"] and viewer_info["note"] != "Tidak ada catatan.":
                    profile_message += f", {viewer_info['note']}"
                # Kirimkan pesan ke pengguna yang memiliki profil (profile_user_id)
                keyboard = [["❤️", "🥱"]]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

                if viewer_photo:
                    # Jika ada foto, kirimkan foto bersama pesan
                    with open(viewer_photo, 'rb') as photo_file:
                        await update.message.reply_photo(photo=photo_file, caption=profile_message, reply_markup=reply_markup)
                else:
                    # Jika tidak ada foto, hanya kirim pesan teks
                    await update.message.reply_text(profile_message, reply_markup=reply_markup)
            except Exception as e:
                await update.message.reply_text(f"Terjadi kesalahan: {str(e)}")

            break
    else:
        await update.message.reply_text("Tidak ada data like yang ditemukan.")
        

        
async def berikan_username(update: Update, context: CallbackContext):
    # Periksa apakah pesan yang diterima adalah "❤️"
    if update.message.text != "❤️":
        return  # Hentikan eksekusi fungsi jika teks tidak sesuai

    # ID pengguna yang memiliki profil (profile_user_id)
    profile_user_id = update.message.from_user.id

    # Memuat data like dari file JSON
    likes_data = load_like_data_user()

    keyboard = [
        ["Lihat Profil Orang"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    # Mencari data like untuk profile_user_id dalam list likes_data
    for like_info in likes_data:
        # Pastikan bahwa selected_user_id adalah integer sebelum perbandingan
        selected_user_id = int(like_info["selected_user_id"])

        # Cek apakah selected_user_id dalam like_info adalah profile_user_id
        if selected_user_id == profile_user_id:
            viewer_user_id = like_info["viewer_user_id"]
            viewer_username = like_info["viewer_username"]
            selected_user_username = like_info["selected_user_username"]

            # Mendapatkan informasi profil pengguna yang memberi like
            try:
                viewer_user = await context.bot.get_chat(viewer_user_id)
                select_user = await context.bot.get_chat(selected_user_id)

                # Informasi profil viewer (pengguna yang memberi like)
                viewer_first_name = viewer_user.first_name
                viewer_last_name = viewer_user.last_name if viewer_user.last_name else ""
                viewer_full_name = f"{viewer_first_name} {viewer_last_name}".strip()
                selected_first_name = select_user.first_name

            except Exception as e:
                viewer_full_name = "Pengguna tidak ditemukan"

            # Kirimkan pesan ke pengguna yang memiliki profil (profile_user_id)
            if viewer_username and selected_user_username:
                # Menyusun pesan profil pengguna yang dipilih secara acak
                message = f"""Sekarang anda dapat mengobrol secara langsung dengan 
👉 <a href='https://t.me/{viewer_username}'>{viewer_first_name}</a>"""
                
                # Kirim pesan ke pengguna yang memiliki profil (profile_user_id)
                await context.bot.send_message(
                    chat_id=profile_user_id,
                    text=message, parse_mode=ParseMode.HTML, reply_markup=reply_markup
                )

                message_1 = f"""Kamu pernah menyukai profil seseorang apakah masih ingat?
                                
Dia memberikan respon dan ingin mengobrol langsung dengan mu. Ini profilnya
👉 <a href='https://t.me/{selected_user_username}'>{selected_first_name}</a>"""

                # Kirim pesan ke pengguna yang memberi like (viewer)
                await context.bot.send_message(
                    chat_id=viewer_user_id,
                    text=message_1, parse_mode=ParseMode.HTML, reply_markup=reply_markup
                )
                try:
                    # Hapus data like dari file JSON
                    likes_data.remove(like_info)
                    save_data_like_user(likes_data)
                except:
                    None

async def delete_data_like_user(update: Update, context: CallbackContext):
    # Periksa apakah pesan yang diterima adalah "🥱"
    if update.message.text != "🥱":
        return  # Hentikan eksekusi fungsi jika teks tidak sesuai

    # Memuat data like dari file JSON
    likes_data = load_like_data_user()

    # Mencari data like untuk profile_user_id dalam list likes_data
    for like_info in likes_data:
        keyboard = [
        ["Lihat Profil Orang"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        # Hapus data like dari file JSON
        likes_data.remove(like_info)
        save_data_like_user(likes_data)
        await update.message.reply_text(text= "Silahkan untuk melihat pengguna yang lain dengan menekan 'Lihat Profile'", reply_markup=reply_markup)

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


async def save_data_room_user(room_data):
    try:
        with open('rooms_data_user.json', 'w', encoding='utf-8') as file:
            json.dump(room_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving room data: {e}")

async def load_data_room_user():
    try:
        with open('rooms_data_user.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("File not found, returning empty list.")
        return []  # Jika file tidak ada, return list kosong
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []  # Jika file JSON rusak, return list kosong
    
async def tambahkan_data_room_user(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username):
    viewer_user_id = str(viewer_user_id)
    selected_user_id = str(selected_user_id)
    
    rooms_data = await load_data_room_user()

    new_rooms_data = {
        "room_id": room_id,
        "viewer_user_id": viewer_user_id,
        "viewer_username": viewer_username,
        "selected_user_id": selected_user_id,
        "selected_user_username": selected_user_username
    }

    rooms_data.append(new_rooms_data)
    await save_data_room_user(rooms_data)
    

# Fungsi untuk membuat ID room unik berdasarkan ID pengguna
def create_room_id(viewer_user_id, selected_user_id):
    room_string = str(viewer_user_id) + str(selected_user_id)
    return hashlib.md5(room_string.encode()).hexdigest()


async def creat_room(update: Update, context: CallbackContext):

    viewer_user_id = update.message.from_user.id  # ID pengguna yang memberi like (viewer)
    viewer_username = update.message.from_user.username  # Username pengguna yang memberi like
    
    # Mendapatkan ID pengguna yang disukai dari context
    selected_user_id = context.user_data.get('selected_user_id')

    await Lihat_Profil_Orang(update, context)
    
    if selected_user_id:
        # Ambil username pengguna yang disukai
        selected_user_username = get_username_by_user_id(selected_user_id)
        
        if selected_user_username:
            # Memperbarui atau menambahkan data like ke file JSON
            room_id = create_room_id(viewer_user_id, selected_user_id)
            
            await tambahkan_data_room_user(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username)
            
            # Hitung jumlah orang yang menyukai pengguna yang dipilih
            room_count = count_room_for_user(selected_user_id)  # Fungsi untuk menghitung jumlah likes
            
            # Kirimkan pesan ke pemilik profil yang disukai (Pengguna 2)
            message = f"Ada {room_count} orang yang ingin membuat room dengan kamu, tampilkan dia?"

            keyboard = [
                ["Coba Lihat 🚀"]
            ]
            pesan = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await context.bot.send_message(chat_id=selected_user_id, text=message, reply_markup=pesan)
        else:
            await update.message.reply_text("Pengguna yang disukai tidak memiliki username.")
    else:
        None

# Fungsi untuk menampilkan data like
async def Coba_Liat_creat_room(update: Update, context: CallbackContext):

    # ID pengguna yang memiliki profil (profile_user_id)
    profile_user_id = update.message.from_user.id

    # Memuat data like dari file JSON
    rooms_data = await load_data_room_user()

    # Mencari data like untuk profile_user_id dalam list likes_data
    for like_info in rooms_data:
        # Mengonversi selected_user_id menjadi integer untuk perbandingan
        selected_user_id = int(like_info["selected_user_id"])

        # Cek apakah selected_user_id dalam like_info adalah profile_user_id
        if selected_user_id == profile_user_id:
            viewer_user_id = like_info["viewer_user_id"]

            # Mendapatkan informasi profil pengguna yang memberi like
            try:
                # Mengambil data diri pengguna yang memberi like dari userdata.json
                user_data = load_user_data()

                # Pastikan data pengguna ada dalam file
                if str(viewer_user_id) in user_data:  # Mengonversi viewer_user_id menjadi string jika diperlukan
                    viewer_info = user_data[str(viewer_user_id)]  # Mengambil data pengguna berdasarkan ID yang tepat
                    viewer_full_name = viewer_info.get("name")
                    viewer_age = viewer_info.get("age")
                    viewer_gender = viewer_info.get("gender")
                    viewer_province = viewer_info.get("province")
                    viewer_city = viewer_info.get("city")
                    viewer_photo = viewer_info.get("photo", None)  # Bisa berupa path foto jika ada

                profile_message = f"{viewer_full_name}, {viewer_age}, {viewer_gender}, {viewer_province}, {viewer_city}"

                if 'note' in viewer_info and viewer_info["note"] and viewer_info["note"] != "Tidak ada catatan.":
                    profile_message += f", {viewer_info['note']}"
                # Kirimkan pesan ke pengguna yang memiliki profil (profile_user_id)
                keyboard = [["🚀", "🥱"]]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

                if viewer_photo:
                    # Jika ada foto, kirimkan foto bersama pesan
                    with open(viewer_photo, 'rb') as photo_file:
                        await update.message.reply_photo(photo=photo_file, caption=profile_message, reply_markup=reply_markup)
                else:
                    # Jika tidak ada foto, hanya kirim pesan teks
                    await update.message.reply_text(profile_message, reply_markup=reply_markup)
            except Exception as e:
                await update.message.reply_text(f"Terjadi kesalahan: {str(e)}")

            break
    else:
        print("kenapa")
        
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
async def tambahkan_data_room_user_ke_bot1(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username):
    viewer_user_id = str(viewer_user_id)
    selected_user_id = str(selected_user_id)
    
    rooms_data = await load_MatchDay_room1()

    new_rooms_data = [
        room_id,
        viewer_user_id,
        selected_user_id,
    ]
    rooms_data.append(new_rooms_data)
    await save_data_room_user1(rooms_data)
    
async def save_data_room_user1(room_data):
    try:
        with open('MatchDay_room1.json', 'w', encoding='utf-8') as file:
            json.dump(room_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving room data: {e}")
        
async def load_MatchDay_room1(filename='MatchDay_room1.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)  # Mengembalikan data yang dimuat
    except FileNotFoundError:
        print("File tidak ditemukan.")
        return []  # Kembalikan list kosong jika file tidak ditemukan
    except json.JSONDecodeError:

        return []
    
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


async def tambahkan_data_room_user_ke_bot2(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username):
    viewer_user_id = str(viewer_user_id)
    selected_user_id = str(selected_user_id)
    
    rooms_data = await load_MatchDay_room2()

    new_rooms_data = [
        room_id,
        viewer_user_id,
        selected_user_id,
    ]
    rooms_data.append(new_rooms_data)
    await save_data_room_user2(rooms_data)
    
async def save_data_room_user2(room_data):
    try:
        with open('MatchDay_room2.json', 'w', encoding='utf-8') as file:
            json.dump(room_data, file, ensure_ascii=False, indent=4)
        print("Data berhasil disimpan di room2.")
    except Exception as e:
        print(f"Error saving room data: {e}")
        
async def load_MatchDay_room2(filename='MatchDay_room2.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)  # Mengembalikan data yang dimuat
    except FileNotFoundError:
        print("File tidak ditemukan.")
        return []  # Kembalikan list kosong jika file tidak ditemukan
    except json.JSONDecodeError:
        return []
    
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


async def tambahkan_data_room_user_ke_bot3(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username):
    viewer_user_id = str(viewer_user_id)
    selected_user_id = str(selected_user_id)
    
    rooms_data = await load_MatchDay_room3()

    new_rooms_data = {
        room_id,
        viewer_user_id,
        selected_user_id,
    }
    rooms_data.append(new_rooms_data)
    await save_data_room_user3(rooms_data)
    
async def save_data_room_user3(room_data):
    try:
        with open('MatchDay_room3.json', 'w', encoding='utf-8') as file:
            json.dump(room_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving room data: {e}")
        
async def load_MatchDay_room3(filename='MatchDay_room3.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)  # Mengembalikan data yang dimuat
    except FileNotFoundError:
        print("File tidak ditemukan.")
        return []  # Kembalikan list kosong jika file tidak ditemukan
    except json.JSONDecodeError:
        return []
    
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


async def tambahkan_data_room_user_ke_bot4(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username):
    viewer_user_id = str(viewer_user_id)
    selected_user_id = str(selected_user_id)
    
    rooms_data = await load_MatchDay_room4()

    new_rooms_data = {
        room_id,
        viewer_user_id,
        selected_user_id,
    }
    rooms_data.append(new_rooms_data)
    await save_data_room_user4(rooms_data)
    
async def save_data_room_user4(room_data):
    try:
        with open('MatchDay_room4.json', 'w', encoding='utf-8') as file:
            json.dump(room_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving room data: {e}")
        
async def load_MatchDay_room4(filename='MatchDay_room4.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)  # Mengembalikan data yang dimuat
    except FileNotFoundError:
        print("File tidak ditemukan.")
        return []  # Kembalikan list kosong jika file tidak ditemukan
    except json.JSONDecodeError:
        return []
    
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


async def tambahkan_data_room_user_ke_bot5(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username):
    viewer_user_id = str(viewer_user_id)
    selected_user_id = str(selected_user_id)
    
    rooms_data = await load_MatchDay_room5()

    new_rooms_data = {
        room_id,
        viewer_user_id,
        selected_user_id,
    }
    rooms_data.append(new_rooms_data)
    await save_data_room_user5(rooms_data)
    
async def save_data_room_user5(room_data):
    try:
        with open('MatchDay_room5.json', 'w', encoding='utf-8') as file:
            json.dump(room_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving room data: {e}")
        
async def load_MatchDay_room5(filename='MatchDay_room5.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)  # Mengembalikan data yang dimuat
    except FileNotFoundError:
        print("File tidak ditemukan.")
        return []  # Kembalikan list kosong jika file tidak ditemukan
    except json.JSONDecodeError:
        return []
    
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


async def tambahkan_data_room_user_ke_bot6(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username):
    viewer_user_id = str(viewer_user_id)
    selected_user_id = str(selected_user_id)
    
    rooms_data = await load_MatchDay_room6()

    new_rooms_data = {
        room_id,
        viewer_user_id,
        selected_user_id,
    }
    rooms_data.append(new_rooms_data)
    await save_data_room_user6(rooms_data)
    
async def save_data_room_user6(room_data):
    try:
        with open('MatchDay_room6.json', 'w', encoding='utf-8') as file:
            json.dump(room_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving room data: {e}")
        
async def load_MatchDay_room6(filename='MatchDay_room6.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)  # Mengembalikan data yang dimuat
    except FileNotFoundError:
        print("File tidak ditemukan.")
        return []  # Kembalikan list kosong jika file tidak ditemukan
    except json.JSONDecodeError:
        return []
    
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


async def tambahkan_data_room_user_ke_bot7(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username):
    viewer_user_id = str(viewer_user_id)
    selected_user_id = str(selected_user_id)
    
    rooms_data = await load_MatchDay_room7()

    new_rooms_data = {
        room_id,
        viewer_user_id,
        selected_user_id,
    }
    rooms_data.append(new_rooms_data)
    await save_data_room_user7(rooms_data)
    
async def save_data_room_user7(room_data):
    try:
        with open('MatchDay_room7.json', 'w', encoding='utf-8') as file:
            json.dump(room_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving room data: {e}")
        
async def load_MatchDay_room7(filename='MatchDay_room7.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)  # Mengembalikan data yang dimuat
    except FileNotFoundError:
        print("File tidak ditemukan.")
        return []  # Kembalikan list kosong jika file tidak ditemukan
    except json.JSONDecodeError:
        return []
    
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


async def tambahkan_data_room_user_ke_bot8(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username):
    viewer_user_id = str(viewer_user_id)
    selected_user_id = str(selected_user_id)
    
    rooms_data = await load_MatchDay_room8()

    new_rooms_data = {
        room_id,
        viewer_user_id,
        selected_user_id,
    }
    rooms_data.append(new_rooms_data)
    await save_data_room_user8(rooms_data)
    
async def save_data_room_user8(room_data):
    try:
        with open('MatchDay_room8.json', 'w', encoding='utf-8') as file:
            json.dump(room_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving room data: {e}")
        
async def load_MatchDay_room8(filename='MatchDay_room8.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)  # Mengembalikan data yang dimuat
    except FileNotFoundError:
        print("File tidak ditemukan.")
        return []  # Kembalikan list kosong jika file tidak ditemukan
    except json.JSONDecodeError:
        return []
    
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


async def tambahkan_data_room_user_ke_bot9(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username):
    viewer_user_id = str(viewer_user_id)
    selected_user_id = str(selected_user_id)
    
    rooms_data = await load_MatchDay_room9()

    new_rooms_data = {
        room_id,
        viewer_user_id,
        selected_user_id,
    }
    rooms_data.append(new_rooms_data)
    await save_data_room_user9(rooms_data)
    
async def save_data_room_user9(room_data):
    try:
        with open('MatchDay_room9.json', 'w', encoding='utf-8') as file:
            json.dump(room_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving room data: {e}")
        
async def load_MatchDay_room9(filename='MatchDay_room9.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)  # Mengembalikan data yang dimuat
    except FileNotFoundError:
        print("File tidak ditemukan.")
        return []  # Kembalikan list kosong jika file tidak ditemukan
    except json.JSONDecodeError:
        return []
    
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


async def tambahkan_data_room_user_ke_bot10(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username):
    viewer_user_id = str(viewer_user_id)
    selected_user_id = str(selected_user_id)
    
    rooms_data = await load_MatchDay_room10()

    new_rooms_data = {
        room_id,
        viewer_user_id,
        selected_user_id,
    }
    rooms_data.append(new_rooms_data)
    await save_data_room_user10(rooms_data)
    
async def save_data_room_user10(room_data):
    try:
        with open('MatchDay_room10.json', 'w', encoding='utf-8') as file:
            json.dump(room_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving room data: {e}")
        
async def load_MatchDay_room10(filename='MatchDay_room10.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)  # Mengembalikan data yang dimuat
    except FileNotFoundError:
        print("File tidak ditemukan.")
        return []  # Kembalikan list kosong jika file tidak ditemukan
    except json.JSONDecodeError:
        return []


# Fungsi utama untuk proses pembuatan room
async def create_room_final(update: Update, context: CallbackContext):
    profile_user_id = update.message.from_user.id  # ID pengguna yang mengirimkan pesan
    
    # Memuat data awal dari file atau sumber lain
    room_data = await load_data_room_user()  # Fungsi untuk memuat data awal
    data_MatchDay_room1 = await load_MatchDay_room1()  # Memuat data MatchDay_room1

    for room_info in room_data:
        # Ambil nilai dari data room
        selected_user_id = str(room_info["selected_user_id"])  # Mengonversi ke string
        
        # Memeriksa apakah selected_user_id sesuai dengan profile_user_id
        if selected_user_id == str(profile_user_id):  # Mengonversi profile_user_id ke string
            viewer_user_id = room_info["viewer_user_id"]
            viewer_username = room_info["viewer_username"]
            selected_user_username = room_info["selected_user_username"]
            room_id = room_info["room_id"]
            keyboard = [
            ["Lihat Profil Orang"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            if viewer_username and selected_user_username:
                # Memeriksa apakah ID yang diinginkan tidak ada dalam data yang dimuat
                if not any(
                    room[0] == room_id or room[1] == viewer_user_id or room[2] == selected_user_id
                    for room in data_MatchDay_room1
                ):
                    deep_link = f"https://t.me/MatchDay_room1_bot?start={room_id}"
                    await context.bot.send_message(chat_id=profile_user_id, text=deep_link, reply_markup=reply_markup)
                    await context.bot.send_message(chat_id=viewer_user_id, text=deep_link, reply_markup=reply_markup)
                    await tambahkan_data_room_user_ke_bot1(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username)
                    try:
                        # Menghapus room_info dari room_data_early
                        room_data = [room for room in room_data if room != room_info]

                        # Menyimpan data yang telah dimodifikasi (setelah penghapusan)
                        await save_data_room_user(room_data)
                        return
                    except Exception as e:
                        print(f"Gagal menghapus dan menyimpan data: {e}")
                else:
                    print("salah")
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

                    data_MatchDay_room2 = await load_MatchDay_room2()
                    
                    if not any(
                        room[0] == room_id or room[1] == viewer_user_id or room[2] == selected_user_id
                        for room in data_MatchDay_room2
                    ):
                        deep_link = f"https://t.me/MatchDay_room2_bot?start={room_id}"
                        await context.bot.send_message(chat_id=profile_user_id, text=deep_link, reply_markup=reply_markup)
                        await context.bot.send_message(chat_id=viewer_user_id, text=deep_link, reply_markup=reply_markup)
                        await tambahkan_data_room_user_ke_bot2(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username)
                        try:
                           # Menghapus room_info dari room_data_early
                            room_data = [room for room in room_data if room != room_info]

                            # Menyimpan data yang telah dimodifikasi (setelah penghapusan)
                            await save_data_room_user(room_data)
                            return
                        except Exception as e:
                            print(f"Gagal menghapus dan menyimpan data: {e}")
                    else:

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                        
                        data_MatchDay_room3 = await load_MatchDay_room3()
                    
                        if not any(
                            room["room_id"] == room_id or room["viewer_user_id"] == viewer_user_id or room["selected_user_id"] == selected_user_id
                            for room in data_MatchDay_room3
                        ):
                            deep_link = f"https://t.me/MatchDay_room3_bot?start={room_id}"
                            await context.bot.send_message(chat_id=profile_user_id, text=deep_link, reply_markup=reply_markup)
                            await context.bot.send_message(chat_id=viewer_user_id, text=deep_link, reply_markup=reply_markup)
                            await tambahkan_data_room_user_ke_bot3(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username)
                            try:
                               # Menghapus room_info dari room_data_early
                                room_data = [room for room in room_data if room != room_info]

                                # Menyimpan data yang telah dimodifikasi (setelah penghapusan)
                                await save_data_room_user(room_data)
                                return
                            except Exception as e:
                                print(f"Gagal menghapus dan menyimpan data: {e}")
                        else:

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                            
                            data_MatchDay_room4 = await load_MatchDay_room4()
                    
                            if not any(
                                room["room_id"] == room_id or room["viewer_user_id"] == viewer_user_id or room["selected_user_id"] == selected_user_id
                                for room in data_MatchDay_room4
                            ):
                                deep_link = f"https://t.me/MatchDay_room4_bot?start={room_id}"
                                await context.bot.send_message(chat_id=profile_user_id, text=deep_link, reply_markup=reply_markup)
                                await context.bot.send_message(chat_id=viewer_user_id, text=deep_link, reply_markup=reply_markup)
                                await tambahkan_data_room_user_ke_bot4(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username)
                                try:
                                   # Menghapus room_info dari room_data_early
                                    room_data = [room for room in room_data if room != room_info]

                                    # Menyimpan data yang telah dimodifikasi (setelah penghapusan)
                                    await save_data_room_user(room_data)
                                    return
                                except Exception as e:
                                    print(f"Gagal menghapus dan menyimpan data: {e}")
                            else:
                                
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                                data_MatchDay_room5 = await load_MatchDay_room5()
                    
                                if not any(
                                    room["room_id"] == room_id or room["viewer_user_id"] == viewer_user_id or room["selected_user_id"] == selected_user_id
                                    for room in data_MatchDay_room5
                                ):
                                    deep_link = f"https://t.me/MatchDay_room5_bot?start={room_id}"
                                    await context.bot.send_message(chat_id=profile_user_id, text=deep_link, reply_markup=reply_markup)
                                    await context.bot.send_message(chat_id=viewer_user_id, text=deep_link, reply_markup=reply_markup)
                                    await tambahkan_data_room_user_ke_bot5(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username)
                                    try:
                                      # Menghapus room_info dari room_data_early
                                        room_data = [room for room in room_data if room != room_info]

                                        # Menyimpan data yang telah dimodifikasi (setelah penghapusan)
                                        await save_data_room_user(room_data)
                                        return
                                    except Exception as e:
                                        print(f"Gagal menghapus dan menyimpan data: {e}")
                                else:
                                    
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                                    
                                    data_MatchDay_room6 = await load_MatchDay_room6()
                    
                                    if not any(
                                        room["room_id"] == room_id or room["viewer_user_id"] == viewer_user_id or room["selected_user_id"] == selected_user_id
                                        for room in data_MatchDay_room6
                                    ):
                                        deep_link = f"https://t.me/MatchDay_room6_bot?start={room_id}"
                                        await context.bot.send_message(chat_id=profile_user_id, text=deep_link, reply_markup=reply_markup)
                                        await context.bot.send_message(chat_id=viewer_user_id, text=deep_link, reply_markup=reply_markup)
                                        await tambahkan_data_room_user_ke_bot6(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username)
                                        try:
                                          # Menghapus room_info dari room_data_early
                                            room_data = [room for room in room_data if room != room_info]

                                            # Menyimpan data yang telah dimodifikasi (setelah penghapusan)
                                            await save_data_room_user(room_data)

                                            return
                                        except Exception as e:
                                            print(f"Gagal menghapus dan menyimpan data: {e}")
                                    else:
                                        
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                                    
                                        data_MatchDay_room7 = await load_MatchDay_room7()
                    
                                    if not any(
                                        room["room_id"] == room_id or room["viewer_user_id"] == viewer_user_id or room["selected_user_id"] == selected_user_id
                                        for room in data_MatchDay_room7
                                    ):
                                        deep_link = f"https://t.me/MatchDay_room7_bot?start={room_id}"
                                        await context.bot.send_message(chat_id=profile_user_id, text=deep_link, reply_markup=reply_markup)
                                        await context.bot.send_message(chat_id=viewer_user_id, text=deep_link, reply_markup=reply_markup)
                                        await tambahkan_data_room_user_ke_bot7(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username)
                                        try:
                                          # Menghapus room_info dari room_data_early
                                            room_data = [room for room in room_data if room != room_info]

                                            # Menyimpan data yang telah dimodifikasi (setelah penghapusan)
                                            await save_data_room_user(room_data)
                                            return
                                        except Exception as e:
                                            print(f"Gagal menghapus dan menyimpan data: {e}")
                                    else:
                            
                                        
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                                    
                                        data_MatchDay_room8 = await load_MatchDay_room8()
                    
                                        if not any(
                                            room["room_id"] == room_id or room["viewer_user_id"] == viewer_user_id or room["selected_user_id"] == selected_user_id
                                            for room in data_MatchDay_room8
                                        ):
                                            deep_link = f"https://t.me/MatchDay_room8_bot?start={room_id}"
                                            await context.bot.send_message(chat_id=profile_user_id, text=deep_link, reply_markup=reply_markup)
                                            await context.bot.send_message(chat_id=viewer_user_id, text=deep_link, reply_markup=reply_markup)
                                            await tambahkan_data_room_user_ke_bot8(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username)
                                            try:
                                                # Menghapus room_info dari room_data_early
                                                room_data = [room for room in room_data if room != room_info]

                                                # Menyimpan data yang telah dimodifikasi (setelah penghapusan)
                                                await save_data_room_user(room_data)
                                                return
                                            except Exception as e:
                                                print(f"Gagal menghapus dan menyimpan data: {e}")
                                        else:                           
                                        
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                                    
                                            data_MatchDay_room9 = await load_MatchDay_room9()
                    
                                            if not any(
                                                room["room_id"] == room_id or room["viewer_user_id"] == viewer_user_id or room["selected_user_id"] == selected_user_id
                                                for room in data_MatchDay_room9
                                            ):
                                                deep_link = f"https://t.me/MatchDay_room9_bot?start={room_id}"
                                                await context.bot.send_message(chat_id=profile_user_id, text=deep_link, reply_markup=reply_markup)
                                                await context.bot.send_message(chat_id=viewer_user_id, text=deep_link, reply_markup=reply_markup)
                                                await tambahkan_data_room_user_ke_bot9(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username)
                                                try:
                                                  # Menghapus room_info dari room_data_early
                                                    room_data = [room for room in room_data if room != room_info]

                                                    # Menyimpan data yang telah dimodifikasi (setelah penghapusan)
                                                    await save_data_room_user(room_data)
                                                    return
                                                except Exception as e:
                                                    print(f"Gagal menghapus dan menyimpan data: {e}")
                                            else:
                                        
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                                    
                                                data_MatchDay_room10 = await load_MatchDay_room10()
                    
                                                if not any(
                                                    room["room_id"] == room_id or room["viewer_user_id"] == viewer_user_id or room["selected_user_id"] == selected_user_id
                                                    for room in data_MatchDay_room10
                                                ):
                                                    deep_link = f"https://t.me/MatchDay_room10_bot?start={room_id}"
                                                    await context.bot.send_message(chat_id=profile_user_id, text=deep_link, reply_markup=reply_markup)
                                                    await context.bot.send_message(chat_id=viewer_user_id, text=deep_link, reply_markup=reply_markup)
                                                    await tambahkan_data_room_user_ke_bot10(room_id, viewer_user_id, viewer_username, selected_user_id, selected_user_username)
                                                    try:
                                                        # Menghapus room_info dari room_data_early
                                                        room_data = [room for room in room_data if room != room_info]

                                                        # Menyimpan data yang telah dimodifikasi (setelah penghapusan)
                                                        await save_data_room_user(room_data)
                                                        return
                                                    except Exception as e:
                                                        print(f"Gagal menghapus dan menyimpan data: {e}")
                                                else:
                                                    break                                      
            else:
                print("Viewer atau selected user tidak memiliki username.")
                



    
async def handle_message(update: Update, context: CallbackContext):
    message_text = update.message.text.strip()
    # Jika tombol "Edit Profile" ditekan, mulai percakapan
    if message_text == "Edit Profil":
        # Mulai percakapan dari langkah pertama (NAME)
        await update.message.reply_text("Siapa nama kamu?")
        return NAME  # Mulai percakapan dari langkah NAME    
    elif message_text == "Lihat Profil Orang":
        await Lihat_Profil_Orang(update, context)
    elif message_text == "Profil":
        await profile(update, context)
    elif message_text == "Menu":
        await menu(update, context)
    elif message_text == "👌":
        await like(update, context)
    elif message_text == "Coba Lihat 🔥":
        await Coba_Liat_Like(update, context)
    elif message_text == "😪":
        await Lihat_Profil_Orang(update, context)
    elif message_text == "🗣":
        await creat_room(update, context)
    elif message_text == "🥱":
        await delete_data_like_user(update, context)
    elif message_text == "Coba Lihat 🚀":
        await Coba_Liat_creat_room(update, context)
    elif message_text == "🚀":
        await create_room_final(update, context)
    elif message_text == "❤️":
        await berikan_username(update, context)


# Fungsi untuk memuat data dari file JSON
def load_data_from_json1(filename='MatchDay_room1.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan data ke file JSON
def save_data_to_json1(data, filename='MatchDay_room1.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Fungsi untuk memuat status pengguna saat server dimulai
def load_user_state1():
    try:
        with open('user_states1.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan status pengguna ke file JSON
def save_user_state1(room_id, viewer_user_id, selected_user_id):
    user_states = load_user_state1()
    user_states.append([room_id, viewer_user_id, selected_user_id])
    with open('user_states1.json', 'w') as f:
        json.dump(user_states, f)

async def start_bot_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if context.args:
        room_id = context.args[0]
        data = load_data_from_json1()

        print(f"Room ID yang diminta: {room_id}")
        print(f"Data yang dimuat: {data}")

        if not data:
            await update.message.reply_text("Data tidak ditemukan.")
            return

        valid = False
        viewer_user_id = None
        selected_user_id = None

        for entry in data:
            if entry[0] == room_id:
                viewer_user_id = entry[1]
                selected_user_id = entry[2]
                valid = True
                break

        if valid:
            await update.message.reply_text(f"Anda telah bergabung ke room {room_id}.")
            context.user_data['room_id'] = room_id
            context.user_data['user_id'] = user_id
            context.user_data['viewer_user_id'] = viewer_user_id
            context.user_data['selected_user_id'] = selected_user_id
            
            # Simpan status pengguna ke file JSON
            save_user_state1(room_id, viewer_user_id, selected_user_id)
        else:
            await update.message.reply_text(f"Anda tidak memiliki akses ke room {room_id}.")
    else:
        await update.message.reply_text("Silakan berikan parameter 'room_id'.")

async def handle_message1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Cek apakah ada state yang tersimpan di user_states.json
    user_states = load_user_state1()
    room_id = None
    viewer_user_id = None
    selected_user_id = None

    # Temukan room dan pasangan yang sesuai dengan user_id
    for entry in user_states:
        current_room_id, viewer_id, selected_id = entry
        if user_id == viewer_id or user_id == selected_id:
            room_id = current_room_id
            viewer_user_id = viewer_id
            selected_user_id = selected_id
            break  # Keluar setelah menemukan pasangan yang cocok

    # Jika tidak ditemukan pasangan yang valid atau pengguna tidak berada dalam ruangan yang valid
    if room_id is None:
        await update.message.reply_text("Anda belum bergabung dengan ruangan yang valid. Gunakan /start <room_id>.")
        return

    # Verifikasi apakah room_id yang tersimpan di context cocok dengan room_id pengguna
    context_room_id = context.user_data.get('room_id')
    if context_room_id != room_id:
        await update.message.reply_text("Anda tidak berada di dalam ruangan yang sama dengan pasangan Anda.")
        return

    # Jika pengguna berada di dalam ruangan yang valid, simpan data ruangan dan pasangan
    context.user_data['room_id'] = room_id
    context.user_data['viewer_user_id'] = viewer_user_id
    context.user_data['selected_user_id'] = selected_user_id

    print(f"User ID: {user_id}, Room ID: {room_id}, Viewer User ID: {viewer_user_id}, Selected User ID: {selected_user_id}")

    # Mengirim pesan hanya jika pengirimnya adalah viewer atau selected user dalam ruangan yang sama
    if user_id == viewer_user_id:
        # Kirim pesan ke selected_user_id
        await context.bot.send_message(chat_id=selected_user_id, text=update.message.text)
    elif user_id == selected_user_id:
        # Kirim pesan ke viewer_user_id
        await context.bot.send_message(chat_id=viewer_user_id, text=update.message.text)
    else:
        # Jika pengguna tidak termasuk dalam pasangan yang valid
        await update.message.reply_text("Anda tidak dapat mengirim pesan ke pengguna lain selain pasangan Anda.")


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



# Fungsi untuk memuat data dari file JSON
def load_data_from_json2(filename='MatchDay_room2.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan data ke file JSON
def save_data_to_json2(data, filename='MatchDay_room2.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Fungsi untuk memuat status pengguna saat server dimulai
def load_user_state2():
    try:
        with open('user_states2.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan status pengguna ke file JSON
def save_user_state2(room_id, viewer_user_id, selected_user_id):
    user_states = load_user_state2()
    user_states.append([room_id, viewer_user_id, selected_user_id])
    with open('user_states2.json', 'w') as f:
        json.dump(user_states, f)

async def start_bot_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if context.args:
        room_id = context.args[0]
        data = load_data_from_json2()

        print(f"Room ID yang diminta: {room_id}")
        print(f"Data yang dimuat: {data}")

        if not data:
            await update.message.reply_text("Data tidak ditemukan.")
            return

        valid = False
        viewer_user_id = None
        selected_user_id = None

        for entry in data:
            if entry[0] == room_id:
                viewer_user_id = entry[1]
                selected_user_id = entry[2]
                valid = True
                break

        if valid:
            await update.message.reply_text(f"Anda telah bergabung ke room {room_id}.")
            context.user_data['room_id'] = room_id
            context.user_data['user_id'] = user_id
            context.user_data['viewer_user_id'] = viewer_user_id
            context.user_data['selected_user_id'] = selected_user_id
            
            # Simpan status pengguna ke file JSON
            save_user_state2(room_id, viewer_user_id, selected_user_id)
        else:
            await update.message.reply_text(f"Anda tidak memiliki akses ke room {room_id}.")
    else:
        await update.message.reply_text("Silakan berikan parameter 'room_id'.")

async def handle_message2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Cek apakah ada state yang tersimpan di user_states.json
    user_states = load_user_state2()
    room_id = None
    viewer_user_id = None
    selected_user_id = None

    # Temukan room dan pasangan yang sesuai dengan user_id
    for entry in user_states:
        current_room_id, viewer_id, selected_id = entry
        if user_id == viewer_id or user_id == selected_id:
            room_id = current_room_id
            viewer_user_id = viewer_id
            selected_user_id = selected_id
            break  # Keluar setelah menemukan pasangan yang cocok

    # Jika tidak ditemukan pasangan yang valid atau pengguna tidak berada dalam ruangan yang valid
    if room_id is None:
        await update.message.reply_text("Anda belum bergabung dengan ruangan yang valid. Gunakan /start <room_id>.")
        return

    # Verifikasi apakah room_id yang tersimpan di context cocok dengan room_id pengguna
    context_room_id = context.user_data.get('room_id')
    if context_room_id != room_id:
        await update.message.reply_text("Anda tidak berada di dalam ruangan yang sama dengan pasangan Anda.")
        return

    # Jika pengguna berada di dalam ruangan yang valid, simpan data ruangan dan pasangan
    context.user_data['room_id'] = room_id
    context.user_data['viewer_user_id'] = viewer_user_id
    context.user_data['selected_user_id'] = selected_user_id

    print(f"User ID: {user_id}, Room ID: {room_id}, Viewer User ID: {viewer_user_id}, Selected User ID: {selected_user_id}")

    # Mengirim pesan hanya jika pengirimnya adalah viewer atau selected user dalam ruangan yang sama
    if user_id == viewer_user_id:
        # Kirim pesan ke selected_user_id
        await context.bot.send_message(chat_id=selected_user_id, text=update.message.text)
    elif user_id == selected_user_id:
        # Kirim pesan ke viewer_user_id
        await context.bot.send_message(chat_id=viewer_user_id, text=update.message.text)
    else:
        # Jika pengguna tidak termasuk dalam pasangan yang valid
        await update.message.reply_text("Anda tidak dapat mengirim pesan ke pengguna lain selain pasangan Anda.")


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# Fungsi untuk memuat data dari file JSON
def load_data_from_json3(filename='MatchDay_room3.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan data ke file JSON
def save_data_to_json3(data, filename='MatchDay_room3.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Fungsi untuk memuat status pengguna saat server dimulai
def load_user_state3():
    try:
        with open('user_states3.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan status pengguna ke file JSON
def save_user_state3(room_id, viewer_user_id, selected_user_id):
    user_states = load_user_state3()
    user_states.append([room_id, viewer_user_id, selected_user_id])
    with open('user_states3.json', 'w') as f:
        json.dump(user_states, f)

async def start_bot_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if context.args:
        room_id = context.args[0]
        data = load_data_from_json3()

        print(f"Room ID yang diminta: {room_id}")
        print(f"Data yang dimuat: {data}")

        if not data:
            await update.message.reply_text("Data tidak ditemukan.")
            return

        valid = False
        viewer_user_id = None
        selected_user_id = None

        for entry in data:
            if entry[0] == room_id:
                viewer_user_id = entry[1]
                selected_user_id = entry[2]
                valid = True
                break

        if valid:
            await update.message.reply_text(f"Anda telah bergabung ke room {room_id}.")
            context.user_data['room_id'] = room_id
            context.user_data['user_id'] = user_id
            context.user_data['viewer_user_id'] = viewer_user_id
            context.user_data['selected_user_id'] = selected_user_id
            
            # Simpan status pengguna ke file JSON
            save_user_state3(room_id, viewer_user_id, selected_user_id)
        else:
            await update.message.reply_text(f"Anda tidak memiliki akses ke room {room_id}.")
    else:
        await update.message.reply_text("Silakan berikan parameter 'room_id'.")

async def handle_message3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Cek apakah ada state yang tersimpan di user_states.json
    user_states = load_user_state3()
    room_id = None
    viewer_user_id = None
    selected_user_id = None

    # Temukan room dan pasangan yang sesuai dengan user_id
    for entry in user_states:
        current_room_id, viewer_id, selected_id = entry
        if user_id == viewer_id or user_id == selected_id:
            room_id = current_room_id
            viewer_user_id = viewer_id
            selected_user_id = selected_id
            break  # Keluar setelah menemukan pasangan yang cocok

    # Jika tidak ditemukan pasangan yang valid atau pengguna tidak berada dalam ruangan yang valid
    if room_id is None:
        await update.message.reply_text("Anda belum bergabung dengan ruangan yang valid. Gunakan /start <room_id>.")
        return

    # Verifikasi apakah room_id yang tersimpan di context cocok dengan room_id pengguna
    context_room_id = context.user_data.get('room_id')
    if context_room_id != room_id:
        await update.message.reply_text("Anda tidak berada di dalam ruangan yang sama dengan pasangan Anda.")
        return

    # Jika pengguna berada di dalam ruangan yang valid, simpan data ruangan dan pasangan
    context.user_data['room_id'] = room_id
    context.user_data['viewer_user_id'] = viewer_user_id
    context.user_data['selected_user_id'] = selected_user_id

    print(f"User ID: {user_id}, Room ID: {room_id}, Viewer User ID: {viewer_user_id}, Selected User ID: {selected_user_id}")

    # Mengirim pesan hanya jika pengirimnya adalah viewer atau selected user dalam ruangan yang sama
    if user_id == viewer_user_id:
        # Kirim pesan ke selected_user_id
        await context.bot.send_message(chat_id=selected_user_id, text=update.message.text)
    elif user_id == selected_user_id:
        # Kirim pesan ke viewer_user_id
        await context.bot.send_message(chat_id=viewer_user_id, text=update.message.text)
    else:
        # Jika pengguna tidak termasuk dalam pasangan yang valid
        await update.message.reply_text("Anda tidak dapat mengirim pesan ke pengguna lain selain pasangan Anda.")


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# Fungsi untuk memuat data dari file JSON
def load_data_from_json4(filename='MatchDay_room4.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan data ke file JSON
def save_data_to_json4(data, filename='MatchDay_room4.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Fungsi untuk memuat status pengguna saat server dimulai
def load_user_state4():
    try:
        with open('user_states4.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan status pengguna ke file JSON
def save_user_state4(room_id, viewer_user_id, selected_user_id):
    user_states = load_user_state4()
    user_states.append([room_id, viewer_user_id, selected_user_id])
    with open('user_states4.json', 'w') as f:
        json.dump(user_states, f)

async def start_bot_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if context.args:
        room_id = context.args[0]
        data = load_data_from_json4()

        print(f"Room ID yang diminta: {room_id}")
        print(f"Data yang dimuat: {data}")

        if not data:
            await update.message.reply_text("Data tidak ditemukan.")
            return

        valid = False
        viewer_user_id = None
        selected_user_id = None

        for entry in data:
            if entry[0] == room_id:
                viewer_user_id = entry[1]
                selected_user_id = entry[2]
                valid = True
                break

        if valid:
            await update.message.reply_text(f"Anda telah bergabung ke room {room_id}.")
            context.user_data['room_id'] = room_id
            context.user_data['user_id'] = user_id
            context.user_data['viewer_user_id'] = viewer_user_id
            context.user_data['selected_user_id'] = selected_user_id
            
            # Simpan status pengguna ke file JSON
            save_user_state4(room_id, viewer_user_id, selected_user_id)
        else:
            await update.message.reply_text(f"Anda tidak memiliki akses ke room {room_id}.")
    else:
        await update.message.reply_text("Silakan berikan parameter 'room_id'.")

async def handle_message4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Cek apakah ada state yang tersimpan di user_states.json
    user_states = load_user_state4()
    room_id = None
    viewer_user_id = None
    selected_user_id = None

    # Temukan room dan pasangan yang sesuai dengan user_id
    for entry in user_states:
        current_room_id, viewer_id, selected_id = entry
        if user_id == viewer_id or user_id == selected_id:
            room_id = current_room_id
            viewer_user_id = viewer_id
            selected_user_id = selected_id
            break  # Keluar setelah menemukan pasangan yang cocok

    # Jika tidak ditemukan pasangan yang valid atau pengguna tidak berada dalam ruangan yang valid
    if room_id is None:
        await update.message.reply_text("Anda belum bergabung dengan ruangan yang valid. Gunakan /start <room_id>.")
        return

    # Verifikasi apakah room_id yang tersimpan di context cocok dengan room_id pengguna
    context_room_id = context.user_data.get('room_id')
    if context_room_id != room_id:
        await update.message.reply_text("Anda tidak berada di dalam ruangan yang sama dengan pasangan Anda.")
        return

    # Jika pengguna berada di dalam ruangan yang valid, simpan data ruangan dan pasangan
    context.user_data['room_id'] = room_id
    context.user_data['viewer_user_id'] = viewer_user_id
    context.user_data['selected_user_id'] = selected_user_id

    print(f"User ID: {user_id}, Room ID: {room_id}, Viewer User ID: {viewer_user_id}, Selected User ID: {selected_user_id}")

    # Mengirim pesan hanya jika pengirimnya adalah viewer atau selected user dalam ruangan yang sama
    if user_id == viewer_user_id:
        # Kirim pesan ke selected_user_id
        await context.bot.send_message(chat_id=selected_user_id, text=update.message.text)
    elif user_id == selected_user_id:
        # Kirim pesan ke viewer_user_id
        await context.bot.send_message(chat_id=viewer_user_id, text=update.message.text)
    else:
        # Jika pengguna tidak termasuk dalam pasangan yang valid
        await update.message.reply_text("Anda tidak dapat mengirim pesan ke pengguna lain selain pasangan Anda.")


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# Fungsi untuk memuat data dari file JSON
def load_data_from_json5(filename='MatchDay_room5.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan data ke file JSON
def save_data_to_json5(data, filename='MatchDay_room5.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Fungsi untuk memuat status pengguna saat server dimulai
def load_user_state5():
    try:
        with open('user_states5.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan status pengguna ke file JSON
def save_user_state5(room_id, viewer_user_id, selected_user_id):
    user_states = load_user_state5()
    user_states.append([room_id, viewer_user_id, selected_user_id])
    with open('user_states5.json', 'w') as f:
        json.dump(user_states, f)

async def start_bot_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if context.args:
        room_id = context.args[0]
        data = load_data_from_json5()

        print(f"Room ID yang diminta: {room_id}")
        print(f"Data yang dimuat: {data}")

        if not data:
            await update.message.reply_text("Data tidak ditemukan.")
            return

        valid = False
        viewer_user_id = None
        selected_user_id = None

        for entry in data:
            if entry[0] == room_id:
                viewer_user_id = entry[1]
                selected_user_id = entry[2]
                valid = True
                break

        if valid:
            await update.message.reply_text(f"Anda telah bergabung ke room {room_id}.")
            context.user_data['room_id'] = room_id
            context.user_data['user_id'] = user_id
            context.user_data['viewer_user_id'] = viewer_user_id
            context.user_data['selected_user_id'] = selected_user_id
            
            # Simpan status pengguna ke file JSON
            save_user_state5(room_id, viewer_user_id, selected_user_id)
        else:
            await update.message.reply_text(f"Anda tidak memiliki akses ke room {room_id}.")
    else:
        await update.message.reply_text("Silakan berikan parameter 'room_id'.")

async def handle_message5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Cek apakah ada state yang tersimpan di user_states.json
    user_states = load_user_state5()
    room_id = None
    viewer_user_id = None
    selected_user_id = None

    # Temukan room dan pasangan yang sesuai dengan user_id
    for entry in user_states:
        current_room_id, viewer_id, selected_id = entry
        if user_id == viewer_id or user_id == selected_id:
            room_id = current_room_id
            viewer_user_id = viewer_id
            selected_user_id = selected_id
            break  # Keluar setelah menemukan pasangan yang cocok

    # Jika tidak ditemukan pasangan yang valid atau pengguna tidak berada dalam ruangan yang valid
    if room_id is None:
        await update.message.reply_text("Anda belum bergabung dengan ruangan yang valid. Gunakan /start <room_id>.")
        return

    # Verifikasi apakah room_id yang tersimpan di context cocok dengan room_id pengguna
    context_room_id = context.user_data.get('room_id')
    if context_room_id != room_id:
        await update.message.reply_text("Anda tidak berada di dalam ruangan yang sama dengan pasangan Anda.")
        return

    # Jika pengguna berada di dalam ruangan yang valid, simpan data ruangan dan pasangan
    context.user_data['room_id'] = room_id
    context.user_data['viewer_user_id'] = viewer_user_id
    context.user_data['selected_user_id'] = selected_user_id

    print(f"User ID: {user_id}, Room ID: {room_id}, Viewer User ID: {viewer_user_id}, Selected User ID: {selected_user_id}")

    # Mengirim pesan hanya jika pengirimnya adalah viewer atau selected user dalam ruangan yang sama
    if user_id == viewer_user_id:
        # Kirim pesan ke selected_user_id
        await context.bot.send_message(chat_id=selected_user_id, text=update.message.text)
    elif user_id == selected_user_id:
        # Kirim pesan ke viewer_user_id
        await context.bot.send_message(chat_id=viewer_user_id, text=update.message.text)
    else:
        # Jika pengguna tidak termasuk dalam pasangan yang valid
        await update.message.reply_text("Anda tidak dapat mengirim pesan ke pengguna lain selain pasangan Anda.")


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# Fungsi untuk memuat data dari file JSON
def load_data_from_json6(filename='MatchDay_room6.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan data ke file JSON
def save_data_to_json6(data, filename='MatchDay_room6.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Fungsi untuk memuat status pengguna saat server dimulai
def load_user_state6():
    try:
        with open('user_states6.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan status pengguna ke file JSON
def save_user_state6(room_id, viewer_user_id, selected_user_id):
    user_states = load_user_state6()
    user_states.append([room_id, viewer_user_id, selected_user_id])
    with open('user_states6.json', 'w') as f:
        json.dump(user_states, f)

async def start_bot_6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if context.args:
        room_id = context.args[0]
        data = load_data_from_json6()

        print(f"Room ID yang diminta: {room_id}")
        print(f"Data yang dimuat: {data}")

        if not data:
            await update.message.reply_text("Data tidak ditemukan.")
            return

        valid = False
        viewer_user_id = None
        selected_user_id = None

        for entry in data:
            if entry[0] == room_id:
                viewer_user_id = entry[1]
                selected_user_id = entry[2]
                valid = True
                break

        if valid:
            await update.message.reply_text(f"Anda telah bergabung ke room {room_id}.")
            context.user_data['room_id'] = room_id
            context.user_data['user_id'] = user_id
            context.user_data['viewer_user_id'] = viewer_user_id
            context.user_data['selected_user_id'] = selected_user_id
            
            # Simpan status pengguna ke file JSON
            save_user_state6(room_id, viewer_user_id, selected_user_id)
        else:
            await update.message.reply_text(f"Anda tidak memiliki akses ke room {room_id}.")
    else:
        await update.message.reply_text("Silakan berikan parameter 'room_id'.")

async def handle_message6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Cek apakah ada state yang tersimpan di user_states.json
    user_states = load_user_state6()
    room_id = None
    viewer_user_id = None
    selected_user_id = None

    # Temukan room dan pasangan yang sesuai dengan user_id
    for entry in user_states:
        current_room_id, viewer_id, selected_id = entry
        if user_id == viewer_id or user_id == selected_id:
            room_id = current_room_id
            viewer_user_id = viewer_id
            selected_user_id = selected_id
            break  # Keluar setelah menemukan pasangan yang cocok

    # Jika tidak ditemukan pasangan yang valid atau pengguna tidak berada dalam ruangan yang valid
    if room_id is None:
        await update.message.reply_text("Anda belum bergabung dengan ruangan yang valid. Gunakan /start <room_id>.")
        return

    # Verifikasi apakah room_id yang tersimpan di context cocok dengan room_id pengguna
    context_room_id = context.user_data.get('room_id')
    if context_room_id != room_id:
        await update.message.reply_text("Anda tidak berada di dalam ruangan yang sama dengan pasangan Anda.")
        return

    # Jika pengguna berada di dalam ruangan yang valid, simpan data ruangan dan pasangan
    context.user_data['room_id'] = room_id
    context.user_data['viewer_user_id'] = viewer_user_id
    context.user_data['selected_user_id'] = selected_user_id

    print(f"User ID: {user_id}, Room ID: {room_id}, Viewer User ID: {viewer_user_id}, Selected User ID: {selected_user_id}")

    # Mengirim pesan hanya jika pengirimnya adalah viewer atau selected user dalam ruangan yang sama
    if user_id == viewer_user_id:
        # Kirim pesan ke selected_user_id
        await context.bot.send_message(chat_id=selected_user_id, text=update.message.text)
    elif user_id == selected_user_id:
        # Kirim pesan ke viewer_user_id
        await context.bot.send_message(chat_id=viewer_user_id, text=update.message.text)
    else:
        # Jika pengguna tidak termasuk dalam pasangan yang valid
        await update.message.reply_text("Anda tidak dapat mengirim pesan ke pengguna lain selain pasangan Anda.")


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# Fungsi untuk memuat data dari file JSON
def load_data_from_json7(filename='MatchDay_room7.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan data ke file JSON
def save_data_to_json7(data, filename='MatchDay_room7.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Fungsi untuk memuat status pengguna saat server dimulai
def load_user_state7():
    try:
        with open('user_states7.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan status pengguna ke file JSON
def save_user_state7(room_id, viewer_user_id, selected_user_id):
    user_states = load_user_state7()
    user_states.append([room_id, viewer_user_id, selected_user_id])
    with open('user_states7.json', 'w') as f:
        json.dump(user_states, f)

async def start_bot_7(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if context.args:
        room_id = context.args[0]
        data = load_data_from_json7()

        print(f"Room ID yang diminta: {room_id}")
        print(f"Data yang dimuat: {data}")

        if not data:
            await update.message.reply_text("Data tidak ditemukan.")
            return

        valid = False
        viewer_user_id = None
        selected_user_id = None

        for entry in data:
            if entry[0] == room_id:
                viewer_user_id = entry[1]
                selected_user_id = entry[2]
                valid = True
                break

        if valid:
            await update.message.reply_text(f"Anda telah bergabung ke room {room_id}.")
            context.user_data['room_id'] = room_id
            context.user_data['user_id'] = user_id
            context.user_data['viewer_user_id'] = viewer_user_id
            context.user_data['selected_user_id'] = selected_user_id
            
            # Simpan status pengguna ke file JSON
            save_user_state7(room_id, viewer_user_id, selected_user_id)
        else:
            await update.message.reply_text(f"Anda tidak memiliki akses ke room {room_id}.")
    else:
        await update.message.reply_text("Silakan berikan parameter 'room_id'.")

async def handle_message7(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Cek apakah ada state yang tersimpan di user_states.json
    user_states = load_user_state7()
    room_id = None
    viewer_user_id = None
    selected_user_id = None

    # Temukan room dan pasangan yang sesuai dengan user_id
    for entry in user_states:
        current_room_id, viewer_id, selected_id = entry
        if user_id == viewer_id or user_id == selected_id:
            room_id = current_room_id
            viewer_user_id = viewer_id
            selected_user_id = selected_id
            break  # Keluar setelah menemukan pasangan yang cocok

    # Jika tidak ditemukan pasangan yang valid atau pengguna tidak berada dalam ruangan yang valid
    if room_id is None:
        await update.message.reply_text("Anda belum bergabung dengan ruangan yang valid. Gunakan /start <room_id>.")
        return

    # Verifikasi apakah room_id yang tersimpan di context cocok dengan room_id pengguna
    context_room_id = context.user_data.get('room_id')
    if context_room_id != room_id:
        await update.message.reply_text("Anda tidak berada di dalam ruangan yang sama dengan pasangan Anda.")
        return

    # Jika pengguna berada di dalam ruangan yang valid, simpan data ruangan dan pasangan
    context.user_data['room_id'] = room_id
    context.user_data['viewer_user_id'] = viewer_user_id
    context.user_data['selected_user_id'] = selected_user_id

    print(f"User ID: {user_id}, Room ID: {room_id}, Viewer User ID: {viewer_user_id}, Selected User ID: {selected_user_id}")

    # Mengirim pesan hanya jika pengirimnya adalah viewer atau selected user dalam ruangan yang sama
    if user_id == viewer_user_id:
        # Kirim pesan ke selected_user_id
        await context.bot.send_message(chat_id=selected_user_id, text=update.message.text)
    elif user_id == selected_user_id:
        # Kirim pesan ke viewer_user_id
        await context.bot.send_message(chat_id=viewer_user_id, text=update.message.text)
    else:
        # Jika pengguna tidak termasuk dalam pasangan yang valid
        await update.message.reply_text("Anda tidak dapat mengirim pesan ke pengguna lain selain pasangan Anda.")


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# Fungsi untuk memuat data dari file JSON
def load_data_from_json8(filename='MatchDay_room8.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan data ke file JSON
def save_data_to_json8(data, filename='MatchDay_room8.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Fungsi untuk memuat status pengguna saat server dimulai
def load_user_state8():
    try:
        with open('user_states8.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan status pengguna ke file JSON
def save_user_state8(room_id, viewer_user_id, selected_user_id):
    user_states = load_user_state8()
    user_states.append([room_id, viewer_user_id, selected_user_id])
    with open('user_states8.json', 'w') as f:
        json.dump(user_states, f)

async def start_bot_8(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if context.args:
        room_id = context.args[0]
        data = load_data_from_json8()

        print(f"Room ID yang diminta: {room_id}")
        print(f"Data yang dimuat: {data}")

        if not data:
            await update.message.reply_text("Data tidak ditemukan.")
            return

        valid = False
        viewer_user_id = None
        selected_user_id = None

        for entry in data:
            if entry[0] == room_id:
                viewer_user_id = entry[1]
                selected_user_id = entry[2]
                valid = True
                break

        if valid:
            await update.message.reply_text(f"Anda telah bergabung ke room {room_id}.")
            context.user_data['room_id'] = room_id
            context.user_data['user_id'] = user_id
            context.user_data['viewer_user_id'] = viewer_user_id
            context.user_data['selected_user_id'] = selected_user_id
            
            # Simpan status pengguna ke file JSON
            save_user_state8(room_id, viewer_user_id, selected_user_id)
        else:
            await update.message.reply_text(f"Anda tidak memiliki akses ke room {room_id}.")
    else:
        await update.message.reply_text("Silakan berikan parameter 'room_id'.")

async def handle_message8(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Cek apakah ada state yang tersimpan di user_states.json
    user_states = load_user_state8()
    room_id = None
    viewer_user_id = None
    selected_user_id = None

    # Temukan room dan pasangan yang sesuai dengan user_id
    for entry in user_states:
        current_room_id, viewer_id, selected_id = entry
        if user_id == viewer_id or user_id == selected_id:
            room_id = current_room_id
            viewer_user_id = viewer_id
            selected_user_id = selected_id
            break  # Keluar setelah menemukan pasangan yang cocok

    # Jika tidak ditemukan pasangan yang valid atau pengguna tidak berada dalam ruangan yang valid
    if room_id is None:
        await update.message.reply_text("Anda belum bergabung dengan ruangan yang valid. Gunakan /start <room_id>.")
        return

    # Verifikasi apakah room_id yang tersimpan di context cocok dengan room_id pengguna
    context_room_id = context.user_data.get('room_id')
    if context_room_id != room_id:
        await update.message.reply_text("Anda tidak berada di dalam ruangan yang sama dengan pasangan Anda.")
        return

    # Jika pengguna berada di dalam ruangan yang valid, simpan data ruangan dan pasangan
    context.user_data['room_id'] = room_id
    context.user_data['viewer_user_id'] = viewer_user_id
    context.user_data['selected_user_id'] = selected_user_id

    print(f"User ID: {user_id}, Room ID: {room_id}, Viewer User ID: {viewer_user_id}, Selected User ID: {selected_user_id}")

    # Mengirim pesan hanya jika pengirimnya adalah viewer atau selected user dalam ruangan yang sama
    if user_id == viewer_user_id:
        # Kirim pesan ke selected_user_id
        await context.bot.send_message(chat_id=selected_user_id, text=update.message.text)
    elif user_id == selected_user_id:
        # Kirim pesan ke viewer_user_id
        await context.bot.send_message(chat_id=viewer_user_id, text=update.message.text)
    else:
        # Jika pengguna tidak termasuk dalam pasangan yang valid
        await update.message.reply_text("Anda tidak dapat mengirim pesan ke pengguna lain selain pasangan Anda.")


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# Fungsi untuk memuat data dari file JSON
def load_data_from_json9(filename='MatchDay_room9.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan data ke file JSON
def save_data_to_json9(data, filename='MatchDay_room9.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Fungsi untuk memuat status pengguna saat server dimulai
def load_user_state9():
    try:
        with open('user_states9.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan status pengguna ke file JSON
def save_user_state9(room_id, viewer_user_id, selected_user_id):
    user_states = load_user_state9()
    user_states.append([room_id, viewer_user_id, selected_user_id])
    with open('user_states9.json', 'w') as f:
        json.dump(user_states, f)

async def start_bot_9(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if context.args:
        room_id = context.args[0]
        data = load_data_from_json9()

        print(f"Room ID yang diminta: {room_id}")
        print(f"Data yang dimuat: {data}")

        if not data:
            await update.message.reply_text("Data tidak ditemukan.")
            return

        valid = False
        viewer_user_id = None
        selected_user_id = None

        for entry in data:
            if entry[0] == room_id:
                viewer_user_id = entry[1]
                selected_user_id = entry[2]
                valid = True
                break

        if valid:
            await update.message.reply_text(f"Anda telah bergabung ke room {room_id}.")
            context.user_data['room_id'] = room_id
            context.user_data['user_id'] = user_id
            context.user_data['viewer_user_id'] = viewer_user_id
            context.user_data['selected_user_id'] = selected_user_id
            
            # Simpan status pengguna ke file JSON
            save_user_state9(room_id, viewer_user_id, selected_user_id)
        else:
            await update.message.reply_text(f"Anda tidak memiliki akses ke room {room_id}.")
    else:
        await update.message.reply_text("Silakan berikan parameter 'room_id'.")

async def handle_message9(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Cek apakah ada state yang tersimpan di user_states.json
    user_states = load_user_state9()
    room_id = None
    viewer_user_id = None
    selected_user_id = None

    # Temukan room dan pasangan yang sesuai dengan user_id
    for entry in user_states:
        current_room_id, viewer_id, selected_id = entry
        if user_id == viewer_id or user_id == selected_id:
            room_id = current_room_id
            viewer_user_id = viewer_id
            selected_user_id = selected_id
            break  # Keluar setelah menemukan pasangan yang cocok

    # Jika tidak ditemukan pasangan yang valid atau pengguna tidak berada dalam ruangan yang valid
    if room_id is None:
        await update.message.reply_text("Anda belum bergabung dengan ruangan yang valid. Gunakan /start <room_id>.")
        return

    # Verifikasi apakah room_id yang tersimpan di context cocok dengan room_id pengguna
    context_room_id = context.user_data.get('room_id')
    if context_room_id != room_id:
        await update.message.reply_text("Anda tidak berada di dalam ruangan yang sama dengan pasangan Anda.")
        return

    # Jika pengguna berada di dalam ruangan yang valid, simpan data ruangan dan pasangan
    context.user_data['room_id'] = room_id
    context.user_data['viewer_user_id'] = viewer_user_id
    context.user_data['selected_user_id'] = selected_user_id

    print(f"User ID: {user_id}, Room ID: {room_id}, Viewer User ID: {viewer_user_id}, Selected User ID: {selected_user_id}")

    # Mengirim pesan hanya jika pengirimnya adalah viewer atau selected user dalam ruangan yang sama
    if user_id == viewer_user_id:
        # Kirim pesan ke selected_user_id
        await context.bot.send_message(chat_id=selected_user_id, text=update.message.text)
    elif user_id == selected_user_id:
        # Kirim pesan ke viewer_user_id
        await context.bot.send_message(chat_id=viewer_user_id, text=update.message.text)
    else:
        # Jika pengguna tidak termasuk dalam pasangan yang valid
        await update.message.reply_text("Anda tidak dapat mengirim pesan ke pengguna lain selain pasangan Anda.")


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# Fungsi untuk memuat data dari file JSON
def load_data_from_json10(filename='MatchDay_room10.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan data ke file JSON
def save_data_to_json10(data, filename='MatchDay_room10.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Fungsi untuk memuat status pengguna saat server dimulai
def load_user_state10():
    try:
        with open('user_states10.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menyimpan status pengguna ke file JSON
def save_user_state10(room_id, viewer_user_id, selected_user_id):
    user_states = load_user_state10()
    user_states.append([room_id, viewer_user_id, selected_user_id])
    with open('user_states10.json', 'w') as f:
        json.dump(user_states, f)

async def start_bot_10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if context.args:
        room_id = context.args[0]
        data = load_data_from_json10()

        print(f"Room ID yang diminta: {room_id}")
        print(f"Data yang dimuat: {data}")

        if not data:
            await update.message.reply_text("Data tidak ditemukan.")
            return

        valid = False
        viewer_user_id = None
        selected_user_id = None

        for entry in data:
            if entry[0] == room_id:
                viewer_user_id = entry[1]
                selected_user_id = entry[2]
                valid = True
                break

        if valid:
            await update.message.reply_text(f"Anda telah bergabung ke room {room_id}.")
            context.user_data['room_id'] = room_id
            context.user_data['user_id'] = user_id
            context.user_data['viewer_user_id'] = viewer_user_id
            context.user_data['selected_user_id'] = selected_user_id
            
            # Simpan status pengguna ke file JSON
            save_user_state10(room_id, viewer_user_id, selected_user_id)
        else:
            await update.message.reply_text(f"Anda tidak memiliki akses ke room {room_id}.")
    else:
        await update.message.reply_text("Silakan berikan parameter 'room_id'.")

async def handle_message10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Cek apakah ada state yang tersimpan di user_states.json
    user_states = load_user_state10()
    room_id = None
    viewer_user_id = None
    selected_user_id = None

    # Temukan room dan pasangan yang sesuai dengan user_id
    for entry in user_states:
        current_room_id, viewer_id, selected_id = entry
        if user_id == viewer_id or user_id == selected_id:
            room_id = current_room_id
            viewer_user_id = viewer_id
            selected_user_id = selected_id
            break  # Keluar setelah menemukan pasangan yang cocok

    # Jika tidak ditemukan pasangan yang valid atau pengguna tidak berada dalam ruangan yang valid
    if room_id is None:
        await update.message.reply_text("Anda belum bergabung dengan ruangan yang valid. Gunakan /start <room_id>.")
        return

    # Verifikasi apakah room_id yang tersimpan di context cocok dengan room_id pengguna
    context_room_id = context.user_data.get('room_id')
    if context_room_id != room_id:
        await update.message.reply_text("Anda tidak berada di dalam ruangan yang sama dengan pasangan Anda.")
        return

    # Jika pengguna berada di dalam ruangan yang valid, simpan data ruangan dan pasangan
    context.user_data['room_id'] = room_id
    context.user_data['viewer_user_id'] = viewer_user_id
    context.user_data['selected_user_id'] = selected_user_id

    print(f"User ID: {user_id}, Room ID: {room_id}, Viewer User ID: {viewer_user_id}, Selected User ID: {selected_user_id}")

    # Mengirim pesan hanya jika pengirimnya adalah viewer atau selected user dalam ruangan yang sama
    if user_id == viewer_user_id:
        # Kirim pesan ke selected_user_id
        await context.bot.send_message(chat_id=selected_user_id, text=update.message.text)
    elif user_id == selected_user_id:
        # Kirim pesan ke viewer_user_id
        await context.bot.send_message(chat_id=viewer_user_id, text=update.message.text)
    else:
        # Jika pengguna tidak termasuk dalam pasangan yang valid
        await update.message.reply_text("Anda tidak dapat mengirim pesan ke pengguna lain selain pasangan Anda.")


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////






# Fungsi untuk menjalankan bot pertama
def run_bot():
    token = '7936535833:AAEDwUcXENZviP8dYoTIA9WBKgUVaPaHgtE'  # Token untuk bot pertama
    application1 = Application.builder().token(token).build()
    
    application1.add_handler(CommandHandler('start', start))
    
    conversation_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        states={
            NAME: [MessageHandler(filters.TEXT, ask_name)],
            AGE: [MessageHandler(filters.TEXT, ask_age)],
            GENDER: [MessageHandler(filters.TEXT, ask_gender)],
            NOTE: [MessageHandler(filters.TEXT, ask_note)],
            ISLAND: [MessageHandler(filters.TEXT, ask_pulau)],
            PROVINCE: [MessageHandler(filters.TEXT, ask_provinsi)],
            CITY: [MessageHandler(filters.TEXT, ask_kota)],
            PHOTO: [MessageHandler(filters.PHOTO, save_photo)],
        },
        fallbacks=[CommandHandler('profil', profile)],
    )
    
    application1.add_handler(conversation_handler)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application1.run_polling())

# Fungsi untuk menjalankan bot pertama
def run_bot1():
    # Ganti dengan token bot pertama
    application1 = Application.builder().token("7435033380:AAGYFMSPfVA3El4swygWu5pA2I9ekRVu8po").build()
    application1.add_handler(CommandHandler("start", start_bot_1))
    application1.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message1))

    
    # Membuat event loop untuk thread ini
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application1.run_polling())

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def run_bot2():
    # Ganti dengan token bot pertama
    application2 = Application.builder().token("7555238128:AAGSbKnWbYix6HRk-_eKgN0ZQh6EqsN_9UE").build()
    application2.add_handler(CommandHandler("start", start_bot_2))
    application2.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message2))

    
    # Membuat event loop untuk thread ini
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application2.run_polling())
    
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def run_bot3():
    # Ganti dengan token bot pertama
    application3 = Application.builder().token("7985572488:AAG20sYpZWVQWxuZ3DuHePn93Ua_XTuGA-A").build()
    application3.add_handler(CommandHandler("start", start_bot_3))
    application3.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message3))

    
    # Membuat event loop untuk thread ini
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application3.run_polling())
    
    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def run_bot4():
    # Ganti dengan token bot pertama
    application4 = Application.builder().token("7826702090:AAHEW9drdbchsL_ExdoNUVuMvZVU3dAWymM").build()
    application4.add_handler(CommandHandler("start", start_bot_4))
    application4.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message4))

    
    # Membuat event loop untuk thread ini
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application4.run_polling())
    
    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def run_bot5():
    # Ganti dengan token bot pertama
    application5 = Application.builder().token("7957352589:AAELBsCZWWz62SPYvoDYPwg_JKKirIPYWY0").build()
    application5.add_handler(CommandHandler("start", start_bot_5))
    application5.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message5))

    
    # Membuat event loop untuk thread ini
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application5.run_polling())
    
    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def run_bot6():
    # Ganti dengan token bot pertama
    application6 = Application.builder().token("7677299719:AAFAcwC6i_WwugC20E661h_dADquNEshVyU").build()
    application6.add_handler(CommandHandler("start", start_bot_6))
    application6.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message6))

    
    # Membuat event loop untuk thread ini
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application6.run_polling())
    
    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def run_bot7():
    # Ganti dengan token bot pertama
    application7 = Application.builder().token("7907237681:AAGtV1XNMrte0cpOl4G6SbHcZ4rVgFbJ6zg").build()
    application7.add_handler(CommandHandler("start", start_bot_7))
    application7.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message7))

    
    # Membuat event loop untuk thread ini
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application7.run_polling())
    
    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def run_bot8():
    # Ganti dengan token bot pertama
    application8 = Application.builder().token("7290772067:AAGOceJMXS9d9NZf-c4UVWMNWzmzywVA4Mo").build()
    application8.add_handler(CommandHandler("start", start_bot_8))
    application8.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message8))

    
    # Membuat event loop untuk thread ini
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application8.run_polling())
    
    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def run_bot9():
    # Ganti dengan token bot pertama
    application9 = Application.builder().token("7694011251:AAHPAuBP7ZF8Uozrfi0PsruQ85y6lFu1zBc").build()
    application9.add_handler(CommandHandler("start", start_bot_9))
    application9.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message9))

    
    # Membuat event loop untuk thread ini
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application9.run_polling())
    
    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def run_bot10():
    # Ganti dengan token bot pertama
    application10 = Application.builder().token("7649005933:AAGR-w2yNGNPyJsbEijZyH9cKz9vAsrX3LM").build()
    application10.add_handler(CommandHandler("start", start_bot_10))
    application10.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message10))

    
    # Membuat event loop untuk thread ini
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application10.run_polling())
    
        
    
    
if __name__ == "__main__":
    # Thread untuk menjalankan bot pertama
    thread = threading.Thread(target=run_bot)
    thread.start()
    
    # Thread untuk menjalankan bot pertama
    thread1 = threading.Thread(target=run_bot1)
    thread1.start()

    # Thread untuk menjalankan bot kedua
    thread2 = threading.Thread(target=run_bot2)
    thread2.start()

    # Thread untuk menjalankan bot kedua
    thread3 = threading.Thread(target=run_bot3)
    thread3.start()

    # Thread untuk menjalankan bot kedua
    thread4 = threading.Thread(target=run_bot4)
    thread4.start()

    # Thread untuk menjalankan bot kedua
    thread5 = threading.Thread(target=run_bot5)
    thread5.start()

    # Thread untuk menjalankan bot kedua
    thread6 = threading.Thread(target=run_bot6)
    thread6.start()

    # Thread untuk menjalankan bot kedua
    thread7 = threading.Thread(target=run_bot7)
    thread7.start()

    # Thread untuk menjalankan bot kedua
    thread8 = threading.Thread(target=run_bot8)
    thread8.start()

    # Thread untuk menjalankan bot kedua
    thread9 = threading.Thread(target=run_bot9)
    thread9.start()

    # Thread untuk menjalankan bot kedua
    thread10 = threading.Thread(target=run_bot10)
    thread10.start()


    # Tunggu sampai kedua bot selesai
    thread.join()
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()
    thread6.join()
    thread7.join()
    thread8.join()
    thread9.join()
    thread10.join()

