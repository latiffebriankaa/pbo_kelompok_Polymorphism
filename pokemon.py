import random
# Daftar nama per rarity dipakai oleh fungsi gacha untuk memilih kartu secara random.
POKEMON_COMMON = ["Rattata", "Pidgey", "bulbasaur", "sqruitle"]
POKEMON_RARE   = ["Pikacu", "Eevee", "Gengar", "Arcerus"]
POKEMON_EPIC   = ["Dragonite", "Mewtwo", "Mew", "Charizard"]


# Parent class: menyimpan atribut umum yang dipakai semua kartu.
class KartuPokemon:
    def __init__(self, nama, hp, damage):
        self.nama = nama
        self.hp = hp
        self.damage = damage

    # Method dasar ini akan dioverride di subclass.
    # Inilah inti polymorphism: nama method sama, hasil berbeda.
    def info_kartu(self):
        return "Informasi kartu belum tersedia."

    def tampilkan(self):
        # Method yang sama dipanggil untuk semua objek kartu.
        # Isi outputnya berubah sesuai class objeknya.
        print(self.info_kartu())


# Subclass Common: kartu paling sering muncul.
class KartuCommon(KartuPokemon):
    def __init__(self, nama):
        # HP dan damage dibuat saat objek dibuat supaya tiap kartu punya stat sendiri.
        super().__init__(nama, hp=random.randint(30, 60), damage=random.randint(10, 25))

    def info_kartu(self):
        # Output sederhana untuk rarity Common.
        return (
            f"\n[COMMON] {self.nama}\n"
            f"HP     : {self.hp}\n"
            f"Damage : {self.damage}\n"
            f"Rarity : COMMON"
        )


# Subclass Rare: lebih kuat dari Common dan punya skill tambahan.
class KartuRare(KartuPokemon):
    def __init__(self, nama):
        super().__init__(nama, hp=random.randint(70, 110), damage=random.randint(30, 55))

    def info_kartu(self):
        # Rare punya skill khusus supaya outputnya terlihat berbeda.
        return (
            f"\n[RARE] {self.nama}\n"
            f"HP     : {self.hp}\n"
            f"Damage : {self.damage}\n"
            f"Skill  : Double Strike\n"
            f"Rarity : RARE"
        )


# Subclass Epic: rarity tertinggi dengan stat paling besar.
class KartuEpic(KartuPokemon):
    def __init__(self, nama):
        super().__init__(nama, hp=random.randint(130, 200), damage=random.randint(70, 120))

    def info_kartu(self):
        # Epic diberi skill lebih banyak agar terasa spesial.
        return (
            f"\n[EPIC] {self.nama}\n"
            f"HP     : {self.hp}\n"
            f"Damage : {self.damage}\n"
            f"Skill  : Mega Evolution\n"
            f"         Ultimate Blast\n"
            f"Rarity : EPIC"
        )


# Fungsi gacha memilih satu kartu berdasarkan peluang rarity.
def gacha_satu_kartu():
    #Menghasilkan 1 kartu secara random berdasarkan probabilitas rarity.
    roll = random.random()  # angka 0.0 - 1.0

    # Common lebih sering muncul, Rare di tengah, Epic paling jarang.
    if roll < 0.60:
        nama  = random.choice(POKEMON_COMMON)
        kartu = KartuCommon(nama)
    elif roll < 0.90:
        nama  = random.choice(POKEMON_RARE)
        kartu = KartuRare(nama)
    else:
        nama  = random.choice(POKEMON_EPIC)
        kartu = KartuEpic(nama)

    return kartu


def single_pull():
    #Pull 1 kartu.
    print("\n SINGLE PULL ")
    kartu = gacha_satu_kartu()
    # Satu method tampilkan() dipakai untuk semua jenis kartu.
    kartu.tampilkan()  # ← polymorphism: info_kartu() berbeda tiap rarity


def multi_pull():
    """Pull 10 kartu sekaligus."""
    print("\n MULTI PULL (10x) ")
    hasil = [gacha_satu_kartu() for _ in range(10)]

    # Ringkasan ini hanya untuk menunjukkan hasil pull per jenis kartu.
    common_count = sum(1 for k in hasil if isinstance(k, KartuCommon))
    rare_count   = sum(1 for k in hasil if isinstance(k, KartuRare))
    epic_count   = sum(1 for k in hasil if isinstance(k, KartuEpic))

    for kartu in hasil:
        # Objek yang berbeda tetap dipanggil dengan method yang sama.
        kartu.tampilkan()  # ← polymorphism dipanggil 10x, hasil beda-beda

    print(f"\nRingkasan: Common={common_count} | Rare={rare_count} | Epic={epic_count}")


# Program utama: menu sederhana agar ada interaksi user.
def main():
    print("-" * 35)
    print("   GACHA KARTU POKEMON")
    print("-" * 35)
    while True:
        print("\n1. Single Pull  (1 x)")
        print("2. Multi Pull   (10 x)")
        print("3. Keluar")

        pilihan = input("\nPilih menu: ").strip()

        if pilihan == "1":
            single_pull()
        elif pilihan == "2":
            multi_pull()
        elif pilihan == "3":
            print("\nSampai jumpa, Trainer!")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")


if __name__ == "__main__":
    main()