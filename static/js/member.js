const orderList = document.querySelector(".historyOrder")
// const src_singleHistoryOrderData = `/api/order/${orderNumber}`

let orderData = "";


// 未登入導回首頁
if (!document.cookie) {
    window.location.replace("/")
}




async function historyOrder() {
    const response = await fetch(`/api/orders`, {
        method: "GET"
    })
    const data = await response.json();
    showHistoryOrder(data)
} historyOrder();



function showHistoryOrder(data) {
    let orderData = data.data

    if (orderData == null) {
        let noHistoryOrderContent = document.createElement("div")
        noHistoryOrderContent.className = "noHistory"
        noHistoryOrderContent.textContent = data.message
        orderList.appendChild(noHistoryOrderContent)
    }
    else {
        for (i = 0; i < orderData.length; i++) {
            let number = orderData[i].ordernumber
            let date = orderData[i].orderdate
            let paymentstatus = orderData[i].paymentstatus
            let price = orderData[i].orderprice

            let historyOrderContent = document.createElement("div")
            historyOrderContent.className = "historyOrder--content"
            orderList.appendChild(historyOrderContent)

            let historyOrderContent0 = document.createElement("div")
            historyOrderContent0.className = "historyOrder--content__item0"
            historyOrderContent0.textContent = number
            historyOrderContent0.addEventListener('click', async function singleHistoryOrder() {
                const historyOrderDetail = document.querySelector(".historyOrderDetail")
                historyOrderDetail.style.display = "flex"

                const response = await fetch(`/api/order/${number}`, {
                    method: "GET"
                });
                const data = await response.json();

                const ordernumber = data.data.number
                const name = data.data.contact.name
                const email = data.data.contact.email
                const phone = data.data.contact.phone
                const date = data.data.trip.date
                const time = data.data.trip.time
                const place = data.data.trip.attraction.name
                const image = data.data.trip.attraction.image

                const orderDetailNumber = document.querySelector(".number")
                const orderDetailName = document.querySelector(".name")
                const orderDetailEmail = document.querySelector(".email")
                const orderDetailPhone = document.querySelector(".phone")
                const orderDetailDate = document.querySelector(".date")
                const orderDetailTime = document.querySelector(".time")
                const orderDetailPlace = document.querySelector(".place")
                const orderDetailImage = document.querySelector(".historyOrderDetail--img")

                orderDetailNumber.textContent = ordernumber
                orderDetailName.textContent = name
                orderDetailEmail.textContent = email
                orderDetailPhone.textContent = phone
                orderDetailDate.textContent = date
                orderDetailImage.setAttribute("src", image)

                if (time === "morning") {
                    orderDetailTime.textContent = "早上9點到下午2點"
                } else {
                    orderDetailTime.textContent = "下午1點到晚上6點"
                }

                orderDetailPlace.textContent = place

            });
            historyOrderContent.appendChild(historyOrderContent0)

            let historyOrderContent1 = document.createElement("div")
            historyOrderContent1.className = "historyOrder--content__item1"
            historyOrderContent1.textContent = date.slice(0, 26)
            historyOrderContent.appendChild(historyOrderContent1)

            let historyOrderContent2 = document.createElement("div")
            historyOrderContent2.className = "historyOrder--content__item2"
            historyOrderContent2.textContent = paymentstatus
            historyOrderContent.appendChild(historyOrderContent2)

            let historyOrderContent3 = document.createElement("div")
            historyOrderContent3.className = "historyOrder--content__item3"
            historyOrderContent3.textContent = price
            historyOrderContent.appendChild(historyOrderContent3)


            document.addEventListener("click", function () {
                let close = document.querySelector(".historyOrderDetail")
                close.style.display = "none";
            }, true)

        }
    }
}

