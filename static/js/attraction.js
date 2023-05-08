// 取得網址路徑景點編號
currentLocation = window.location.origin
let currentPathname = window.location.pathname
let src_singleAttractionData = `${currentLocation}/api${currentPathname}`

const slideshowContainer = document.querySelector(".slideshow-container")


//取得單一景點API資料
function fetchSingleData() {
    fetch(src_singleAttractionData).then(function (response) {
        return response.json();
    }).then(function (data) {
        //console.log(data)
        let singleSpotData = data.data;

        // 分類資料
        let name = singleSpotData.name;
        let category = singleSpotData.category;
        let mrt = singleSpotData.mrt;
        let description = singleSpotData.description;
        let address = singleSpotData.address;
        let transport = singleSpotData.transport;
        let images = singleSpotData.images;

        //文字資料填入頁面
        let spotName = document.querySelector(".spotName");
        spotName.textContent = name;

        let spotCat = document.querySelector(".spotCat");
        spotCat.textContent = category;

        let spotMrt = document.querySelector(".spotMrt");
        spotMrt.textContent = " at  " + mrt;

        let spotContent = document.querySelector(".description");
        spotContent.textContent = description;

        let addressContent = document.querySelector(".address-content");
        addressContent.textContent = address;

        let transportContent = document.querySelector(".transport-content");
        transportContent.textContent = transport;



        //圖片填入頁面
        let slidePicBox = document.querySelector(".slidePicBox");
        let dotBox = document.querySelector(".dot-container");
        for (i = 0; i < images.length; i++) {
            let slidePic = document.createElement("img")
            slidePic.className = "slidePic"
            slidePic.setAttribute("src", images[i])
            slidePicBox.appendChild(slidePic)

            //依據圖片數量顯示圓點
            let dot = document.createElement("span")
            dot.className = "dot"
            dotBox.appendChild(dot)
        }


        // carousel function

        // previous page
        let previous = document.querySelector(".prev");
        previous.addEventListener('click', function () {
            plusSlides(-1);
        });

        //next page
        let next = document.querySelector(".next");
        next.addEventListener('click', function () {
            plusSlides(1);
        });


        let slideIndex = 1;
        showSlides(slideIndex);

        // Next/previous controls
        function plusSlides(n) {
            showSlides(slideIndex += n);
        }


        function showSlides(n) {
            let i;
            let slides = slidePicBox.querySelectorAll('img');
            let dots = dotBox.querySelectorAll(".dot");

            if (n > slides.length) { slideIndex = 1 }
            if (n < 1) { slideIndex = slides.length }

            for (i = 0; i < slides.length; i++) {
                slides[i].style.display = "none";
            }

            for (i = 0; i < dots.length; i++) {
                dots[i].className = dots[i].className.replace(" active", "");
            }

            slides[slideIndex - 1].style.display = "block";
            dots[slideIndex - 1].className += " active";
        }

    })


    // 導覽時段選擇
    let am = document.querySelector("#am")
    am.addEventListener('click', function () {
        let amFee = document.querySelector(".price")
        amFee.textContent = "新台幣2000元"
    })

    let pm = document.querySelector("#pm")
    pm.addEventListener('click', function () {
        let pmFee = document.querySelector(".price")
        pmFee.textContent = "新台幣2500元"
    })

};
fetchSingleData()


//預定行程
let startBooking = document.querySelector(".bookBtn")
//限定只能選擇今日(含)之後的日期
let currentDate = new Date().toISOString().split("T")[0];
document.getElementById("input-date").min = currentDate;

if (document.cookie) {
    startBooking.addEventListener('click', () => {

        let attractionId = location.pathname.slice(12,);
        let date = document.querySelector(".date").value;
        let time = document.querySelector("input[name='pickTime']:checked").value;
        let price = document.querySelector(".price").textContent.slice(3, 7);
        let booking_src = `/api/booking`
        let bookingBody = {
            "attractionId": attractionId,
            "date": date,
            "time": time,
            "price": price,
        }

        if (attractionId && date && time && price) {
            fetch(booking_src, {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(bookingBody),
            }).then((response) => {
                return response.json();
            }).then(data => {
                if (data.ok == true) {
                    window.location.replace("/booking")
                }
                if (data.error == true) {
                    window.alert("建立失敗，輸入不正確或其他原因")
                }
            })

        }
        else {
            window.alert("請確認欄位皆已填寫!")
        }
    }
    )
}
if (!document.cookie) {
    startBooking.addEventListener('click', () => {
        let popLogIn = document.querySelector(".logIn")
        popLogIn.style.display = "flex"
    })
}
