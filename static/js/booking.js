
// 未登入導回首頁
if (!document.cookie) {
    window.location.replace("/")
}

//取得預定行程頁面
function bookingData() {
    fetch(`/api/booking`).then((response) => {
        return response.json();
    }).then(data => {
        let id = data.data.attraction.id;
        let title = data.data.attraction.name;
        let address = data.data.attraction.address;
        let image = data.data.attraction.image;
        let date = data.data.date;
        let time = data.data.time;
        let price = data.data.price;
        let memberName = data.data.memberName;
        let memberEmail = data.data.memberEmail

        let greeting = document.querySelector(".greeting")
        greeting.textContent = "您好， " + memberName + " 待預定的行程如下:"


        if (data.data === null) {
            let mainContent = document.querySelector(".mainContent")
            mainContent.style.display = "none"
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
                detailTime.textContent = "時間：早上9點到下午2點"
            } else {
                detailTime.textContent = "時間：下午1點到晚上6點"
            }

            let detailPrice = document.querySelector(".schedule__detail--price")
            let totalPrice = document.querySelector(".payment__check--price")
            detailPrice.textContent = "費用：" + price + " 元"
            totalPrice.textContent = "總價：新台幣" + price + " 元"

            let detailAddress = document.querySelector(".schedule__detail--place")
            let bookingAddress = "地點：" + address
            detailAddress.textContent = bookingAddress

            let bookingName = document.querySelector("#bookingName")
            bookingName.value = memberName

            let bookingEmail = document.querySelector("#bookingEmail")
            bookingEmail.value = memberEmail

        }

        // 讓 button click 之後觸發 getPrime 方法
        let bookingOrder = document.querySelector(".payment__check--btn")

        bookingOrder.addEventListener('click', () => {
            document.querySelector(".loader").style.display = "block";
        })

        bookingOrder.addEventListener('click', () => {
            const orderName = document.querySelector("#bookingName").value
            const orderEmail = document.querySelector("#bookingEmail").value
            const orderPhone = document.querySelector("#bookingPhone").value

            const emailPattern = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

            if (emailPattern.test(orderEmail)) {
                // Email is valid
            } else {
                window.alert("無效的電子信箱，請重新填寫！");
                window.location.reload();
            }

            const phoneNumberRegex = /^09\d{8}$/;
            if (phoneNumberRegex.test(orderPhone)) {
                // The phone number is in the correct format
                console.log("Valid phone number");
            } else {
                // The phone number is not in the correct format
                window.alert("無效的手機號碼，請重新填寫！");
                window.location.reload();
            }


            // Get prime
            TPDirect.card.getPrime((result) => {
                if (result.status !== 0) {
                    // alert('get prime error ' + result.msg)
                    return
                }

                let orderPrime = result.card.prime
                // alert('get prime 成功，prime: ' + orderPrime)


                orderData = {
                    "prime": orderPrime,
                    "order": {
                        "price": price,
                        "trip": {
                            "attraction": {
                                "id": id,
                                "name": title,
                                "address": address,
                                "image": image = image
                            },
                            "date": date,
                            "time": time,
                        },
                        "contact": {
                            "name": orderName,
                            "email": orderEmail,
                            "phone": orderPhone,
                        }
                    }
                }

                // send prime to your server, to pay with Pay by Prime API .
                async function order() {
                    const response = await fetch(`/api/orders`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify(orderData),
                    });
                    const confirmOrder = await response.json();
                    if (confirmOrder.data) {
                        let orderNumber = confirmOrder.data.number;
                        window.location.replace(`/thankyou?number=${orderNumber}`)
                    }
                    else if (res.error) {
                        window.location.reload();
                    }

                } order();

            })

        })
    })
} bookingData()




// 刪除待預定行程
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

// 串接金流預定行程初始化金鑰
TPDirect.setupSDK(126877, 'app_6PZ8vzKLkBi2tWb1cf5ofZAXiP8gwmnwWBxHxzPLR6AG4MAlewxDBn923QDt', 'sandbox');

let fields = {
    number: {
        // css selector
        element: '#card-number',
        placeholder: '**** **** **** ****'
    },
    expirationDate: {
        // DOM object
        element: document.getElementById('card-expiration-date'),
        placeholder: 'MM / YY'
    },
    ccv: {
        element: '#card-ccv',
        placeholder: 'ccv'
    }
};
// 植入輸入卡號表單
TPDirect.card.setup({
    fields: fields,
    styles: {
        // Style all elements
        'input': {
            'color': 'gray'
        },
        // Styling ccv field
        'input.ccv': {
            // 'font-size': '16px'
        },
        // Styling expiration-date field
        'input.expiration-date': {
            // 'font-size': '16px'
        },
        // Styling card-number field
        'input.card-number': {
            // 'font-size': '16px'
        },
        // style focus state
        ':focus': {
            // 'color': 'black'
        },
        // style valid state
        '.valid': {
            'color': 'green'
        },
        // style invalid state
        '.invalid': {
            'color': 'red'
        },
        // Media queries
        // Note that these apply to the iframe, not the root window.
        '@media screen and (max-width: 400px)': {
            'input': {
                'color': 'orange'
            }
        }
    },
    // 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
    isMaskCreditCardNumber: true,
    maskCreditCardNumberRange: {
        beginIndex: 6,
        endIndex: 11
    }
})





