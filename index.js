var app = new Vue ({
    el: '#app',
    data: {
         message: 'Hola Mision TIC 2022',
         info:[]
    },
    mounted () {
        axios
           .get("http://127.0.0.1:8000/")
           .then(response => (this.info = response.data))
       }
});
