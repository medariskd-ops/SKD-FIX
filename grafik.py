import matplotlib.pyplot as plt
from database import supabase

def tampil_grafik():

    data = supabase.table("users").select("*").execute().data

    nama = [d["nama"] for d in data]
    twk = [d["twk"] for d in data]
    tiu = [d["tiu"] for d in data]
    tkp = [d["tkp"] for d in data]
    total = [d["total"] for d in data]

    # Grafik 1
    plt.figure()
    plt.plot(nama, twk, marker='o', label='TWK', color="#1E293B")
    plt.plot(nama, tiu, marker='o', label='TIU', color="#64748B")
    plt.plot(nama, tkp, marker='o', label='TKP', color="#10B981")

    plt.title("Nilai SKD")
    plt.legend()
    plt.show()

    # Grafik 2
    plt.figure()
    plt.plot(nama, total, marker='o', color="#1E293B")
    plt.title("Total SKD")
    plt.show()
