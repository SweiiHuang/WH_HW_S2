// 未登入導回首頁
if (!document.cookie) {
    window.location.replace("/")
}

const orderNumber = window.location.search.slice(8,)

const order = document.querySelector(".orderNumber")
order.textContent = orderNumber

currentLocation = window.location.origin
const href_member = `${currentLocation}/member`
const member = document.querySelector(".member")
member.setAttribute("href", href_member)