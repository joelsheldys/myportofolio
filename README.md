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