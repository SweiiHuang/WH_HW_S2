// 未登入導回首頁
if (!document.cookie) {
    window.location.replace("/")
}

const orderNumber = window.location.search.slice(8,)

const order = document.querySelector(".orderNumber")
order.textContent = orderNumber