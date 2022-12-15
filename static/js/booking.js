
// 未登入導回首頁
if (!document.cookie) {
    window.location.replace("/")
}

//取得預定行程頁面
function bookingData() {
    fetch(`/api/booking`).then((response) => {
        return response.json();
    }).then(data => {
        console.log(data)

        let id = data.data.attraction.id;
        let title = data.data.attraction.name;
        let address = data.data.attraction.address;
        let image = data.data.attraction.image;
        let date = data.data.date;
        let time = data.data.time;
        let price = data.data.price;
        let memberName = data.data.memberName;

        let greeting = document.querySelector(".greeting")
        greeting.textContent = "您好， " + memberName + " 待預定的行程如下:"


        if (data.data === null) {
            window.location.reload();
        }
        else {

            let mainContent = document.querySelector(".mainContent")
            mainContent.style.display = "block"


            // 載入圖片
            let showImg = document.querySelector(".schedule_pic")
            let detailImg = document.createElement("img")
            detailImg.className = "schedule_pic--img"
            detailImg.setAttribute("src", image)
            showImg.appendChild(detailImg)

            //載入景點名稱
            let detailTitle = document.querySelector(".schedule__detail--title")
            let bookingTitle = "台北一日遊：" + title
            detailTitle.textContent = bookingTitle

            let detailDate = document.querySelector(".schedule__detail--date")
            let bookingDate = "日期：" + date
            detailDate.textContent = bookingDate

            let detailTime = document.querySelector(".schedule__detail--time")
            if (time === "morning") {
                detailTime.textContent = "時間：早上9點到下午4點"
            } else {
                detailTime.textContent = "時間：下午1點到晚上8點"
            }

            let detailPrice = document.querySelector(".schedule__detail--price")
            let totalPrice = document.querySelector(".payment__check--price")
            detailPrice.textContent = "費用：" + price + " 元"
            totalPrice.textContent = "總價：新台幣" + price + " 元"

            let detailAddress = document.querySelector(".schedule__detail--place")
            let bookingAddress = "地點：" + address
            detailAddress.textContent = bookingAddress

        }
    })
} bookingData()


const deleteSchedule = document.querySelector(".schedule__detail--delete")
deleteSchedule.addEventListener('click', () => {
    fetch(`/api/booking`, {
        method: "DELETE"
    }).then((response) => {
        return response.json();
    }).then(data => {
        if (data.ok === true) {
            window.location.reload();
        }
    })
})





