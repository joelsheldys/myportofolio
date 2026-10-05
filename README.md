NAME    : Joel Sheldy Sucipto
NPM     : 2506622494
Kelas   : PBP A
Umur    : 19 tahun

### Tugas 1

1. Ya, saya menggunakan elemen semantik HTML5 dalam merancang struktur website portofolio saya, yaitu <header>, <nav>, <main>, <section>, dan <footer>. Elemen-elemen ini membantu saya dalam membuat struktur coding lebih jelas dan mudah terbaca.
2. Cukup menantang, saya sudah pernah belajar sedikit mengenai css, dan saya hanya mengikuti template web nya saja, tidak menambahkan terlalu banyak dan membuat tambahan yang simpel.
3. Data hanya ditulis di index.html saja, harus diubah manual dan belum memiliki database untuk mengubah data sewaktu-waktu. dari permasalahan itu, kedepannya saya ingin mengembangkan dalam hal model database agar tidak perlu mengubah secara manual dan juga dapat menambahkan data langsung ke halaman, tidak perlu edit html manual.

Pengerjaan Tugas Individu 1 tidak menggunakan AI

### Tugas 2

1. Ketika pengguna membuka halaman Academics, misalnya /academics/, permintaan pertama kali masuk ke urls.py yang ada di project. Di file ini, Django akan melihat bahwa URL tersebut diarahkan ke aplikasi main. Setelah itu, urls.py di dalam aplikasi main akan mencari URL yang sesuai. Untuk /academics/, URL tersebut akan diarahkan ke view show_academics. Di dalam view, Django mengambil data dari model Academic yang tersimpan di database. Setelah data didapatkan, view mengirim data tersebut ke template academics.html. Template kemudian menggunakan data tersebut untuk membuat tampilan HTML. Setelah selesai, HTML dikirim kembali ke browser dan akhirnya pengguna bisa melihat daftar pendidikan pada halaman portofolio.

2. Data portofolio lebih baik disimpan di model karena lebih mudah untuk dikelola. Template seharusnya lebih fokus untuk mengatur tampilan, bukan menyimpan semua data. Misalnya data pendidikan ditulis langsung di academics.html. Kalau ingin menambahkan sekolah baru, kita harus membuka dan mengubah file HTML tersebut. Kalau datanya sudah banyak, cara ini akan cukup merepotkan. Dengan menggunakan model Academic, data disimpan di database. Jadi, ketika ingin menambah atau mengubah data, kita cukup mengubah data di database tanpa harus mengubah template. Template yang sama bisa digunakan untuk menampilkan banyak data. Hal ini membuat aplikasi lebih mudah dirawat dan dikembangkan. Misalnya, nanti ingin menambahkan fitur untuk menambah, mengedit, atau menghapus data pendidikan, kita sudah memiliki struktur database yang bisa digunakan untuk fitur tersebut.

3.  Kedua perintah ini sama-sama berhubungan dengan perubahan model dan database, tetapi fungsinya berbeda. makemigrations digunakan untuk membuat file yang berisi perubahan pada model. Sedangkan migrate digunakan untuk menerapkan perubahan tersebut ke database. Misalnya kita menambahkan model Academic, maka kita perlu menjalankan kedua perintah tersebut agar model yang dibuat di Python juga benar-benar memiliki tabel di database.

Pengerjaan Tugas Individu 2 ini menggunakan AI berupa ChatGPT untuk mengetahui letak error dari code.

### Tugas 3

1. Kita memakai ModelForm alih-alih form HTML manual karena ModelForm otomatis menghasilkan field, validasi, dan widget berdasarkan model yang sudah didefinisikan, jadi tidak perlu menulis ulang struktur field secara manual dan risiko field tidak sinkron dengan model jadi lebih kecil. ModelForm juga otomatis melakukan validasi tipe data serta constraint dari model (misalnya required, max_length), sehingga proses validasi input jadi lebih aman dan konsisten. Sementara itu, {% csrf_token %} wajib ditambahkan karena Django membutuhkan token ini untuk melindungi form dari serangan Cross-Site Request Forgery, token ini memastikan bahwa request POST yang diterima server benar-benar berasal dari form yang dirender oleh aplikasi itu sendiri, bukan dari situs lain yang mencoba mengirim request atas nama pengguna tanpa sepengetahuannya.

2. JSON lebih disukai dibandingkan XML dalam pengembangan aplikasi web modern karena strukturnya lebih ringkas dan lebih mudah dibaca manusia maupun diparsing oleh mesin, sehingga ukuran data yang dikirim lebih kecil dan proses transfer jadi lebih cepat. JSON juga native di JavaScript sehingga tidak butuh parser tambahan di sisi frontend, berbeda dengan XML yang membutuhkan parser XML terpisah dan sintaksnya lebih verbose dengan banyak tag pembuka-penutup. Hampir semua bahasa pemrograman modern serta framework/API modern (termasuk Django) sudah punya dukungan bawaan untuk serialize/deserialize JSON, membuatnya jadi pilihan standar de facto untuk pertukaran data web saat ini.

3. Saat fungsi view dipanggil untuk mengembalikan data dalam bentuk JSON, alurnya dimulai dari view mengambil data dari database melalui model (misalnya Academic.objects.all()), lalu data berupa objek-objek model tersebut diserialisasi menjadi teks JSON menggunakan serializers.serialize("json", ...), dan hasilnya dikembalikan sebagai HttpResponse dengan content_type "application/json" agar browser/klien tahu bahwa isi response adalah JSON. Proses serialization diperlukan karena objek model Django adalah objek Python (instance class) yang tidak bisa langsung dikirim lewat HTTP maupun dibaca oleh klien lain seperti JavaScript; objek tersebut harus diubah dulu ke format teks universal seperti JSON supaya bisa dikirim melalui jaringan dan dipahami oleh sistem lain di luar Django, termasuk saat nanti data itu perlu dideserialisasi kembali menjadi objek untuk ditampilkan di halaman.

Deklarasi AI

Pengerjaan Tugas Individu 3 ini menggunakan AI berupa Claude untuk mengidentifikasi error code

### Tugas 4

Fitur Tambahan 
- Peran: Pengunjung, User biasa, Editor (grup Django `Editor`), Pemilik (superuser)
- Cek hak akses di server (`main/permissions.py`, decorator `role_required`) alurnya: anonim -> redirect login, tidak berhak -> HTTP 403
- Tombol Tambah/Edit/Hapus disembunyikan lewat context processor `main.context_processors.roles`
- Star untuk Academics dan Projects (`ManyToManyField` ke `User`, `toggle_star` via POST + CSRF)
- Endpoint JSON memakai whitelist `fields` agar data user tidak bocor


Deklarasi AI
- Tools: Claude dan ChatGPT
- Cara prompting: memasukkan screenshot halaman error dan traceback, menanyakan asal error
- Bagian yang dibantu AI: checking error

### Tugas 5

1. Jelaskan apa itu debouncing dan mengapa teknik ini penting diterapkan pada fitur pencarian yang menggunakan AJAX!

Debouncing adalah teknik untuk menunda eksekusi suatu fungsi sampai pengguna berhenti melakukan suatu aktivitas selama waktu tertentu. Pada fitur pencarian yang menggunakan AJAX, debouncing digunakan agar request ke server tidak dikirim setiap kali pengguna menekan satu tombol pada keyboard. Misalnya, ketika pengguna mengetik "Universitas", tanpa debouncing browser dapat mengirim request untuk "U", "Un", "Uni", dan seterusnya. Dengan debouncing, request hanya dikirim setelah pengguna berhenti mengetik, misalnya selama 300 milidetik. Teknik ini penting karena dapat mengurangi jumlah request ke server, menghemat penggunaan resource, dan membuat fitur pencarian menjadi lebih efisien.

2. Jelaskan fungsi dari penggunaan await ketika kita menggunakan fetch()! Apa yang akan terjadi jika kita tidak menggunakan await?

`await` digunakan untuk menunggu hasil dari operasi asynchronous seperti `fetch()` sebelum kode berikutnya dijalankan. Pada fitur AJAX, `await fetch()` membuat program menunggu sampai response dari server diterima sehingga response tersebut dapat diperiksa dan diproses, misalnya dengan mengecek `response.ok` atau mengambil data menggunakan `response.json()`. Jika `await` tidak digunakan, `fetch()` akan langsung mengembalikan sebuah Promise, sehingga kode berikutnya dapat berjalan sebelum response dari server tersedia. Akibatnya, kita tidak dapat langsung memperlakukan hasil `fetch()` sebagai response dan proses pengambilan serta penampilan data dapat berjalan tidak sesuai urutan yang diharapkan.

3. Jelaskan apa itu serangan XSS (Cross-Site Scripting) dan mengapa data yang ditampilkan melalui AJAX/JavaScript lebih rentan terhadap serangan ini daripada data yang ditampilkan langsung melalui template Django!

XSS (Cross-Site Scripting) adalah serangan dengan cara menyisipkan kode atau script berbahaya ke dalam data yang kemudian ditampilkan dan dijalankan oleh browser pengguna. Pada data yang ditampilkan melalui AJAX dan JavaScript, nilai dari server sering kali dimasukkan secara dinamis ke dalam halaman. Jika data tersebut langsung dimasukkan sebagai HTML tanpa pengamanan, input berbahaya dapat dianggap sebagai kode HTML atau JavaScript dan dieksekusi oleh browser. Karena itu, setiap data yang ditampilkan melalui JavaScript perlu di-escape, misalnya menggunakan `textContent` atau fungsi `escapeHtml`. Selain itu, input teks juga perlu dibersihkan di sisi server menggunakan `strip_tags` pada ModelForm. Dengan kombinasi sanitasi di server dan escaping saat data dirender oleh JavaScript, risiko XSS dapat dikurangi dan data pengguna dapat ditampilkan sebagai teks biasa. 

### AI Disclosure

Dalam pengerjaan Tugas 5, saya menggunakan ChatGPT sebagai alat bantu untuk memahami instruksi tugas, mencari alternatif implementasi AJAX dan JavaScript, serta membantu menjelaskan error yang muncul selama proses pengembangan. Saya tetap melakukan implementasi, pengujian, dan penyesuaian kode secara manual pada project saya agar sesuai dengan struktur dan kebutuhan website portfolio yang saya kerjakan. Setelah menggunakan saran dari AI, saya memeriksa kembali kode, menjalankan aplikasi, serta melakukan debugging dan perbaikan terhadap bagian yang belum sesuai.