// 登入狀態
let src = `/api/user/auth`
fetch(src, {
    method: "GET"
}).then((response) => {
    return response.json();
}).then(data => {
    let statusCheck = document.querySelector(".topItem")
    if (data.data != null) {
        statusCheck.textContent = "登出系統"
        statusCheck.addEventListener('click', () => {
            fetch(`/api/user/auth`, {
                method: "DELETE"
            }).then((response) => {
                return response.json();
            }).then(data => {
                if (data.ok === true) {
                    window.location.reload();
                    alert("已登出")
                }
            })
        })
    } if (data.data == null) {
        statusCheck.textContent = "登入/註冊"
    };
});



//登入會員視窗
let memberLogIn = document.querySelector(".topItem");
memberLogIn.addEventListener('click', () => {
    let popLogIn = document.querySelector(".logIn")
    popLogIn.style.display = "flex"
})
let closeLogIn = document.querySelector(".logIn__close")
closeLogIn.addEventListener('click', () => {
    let popLogIn = document.querySelector(".logIn")
    popLogIn.style.display = "none"
})

let clickRegister = document.querySelector(".logIn__click")
clickRegister.addEventListener('click', () => {
    let popLogIn = document.querySelector(".logIn")
    popLogIn.style.display = "none"
    let popRegister = document.querySelector(".register")
    popRegister.style.display = "flex"
})


//註冊會員視窗
let closeRegister = document.querySelector(".register__close")
closeRegister.addEventListener('click', () => {
    let popRegister = document.querySelector(".register")
    popRegister.style.display = "none"
})

let clickLogIn = document.querySelector(".register__click")
clickLogIn.addEventListener('click', () => {
    let popRegister = document.querySelector(".register")
    popRegister.style.display = "none"
    let popLogIn = document.querySelector(".logIn")
    popLogIn.style.display = "flex"

})

//會員登入
let logInBtn = document.querySelector(".logIn__btn")
logInBtn.addEventListener('click', () => {
    let email = document.querySelector(".logIn__email").value;
    let password = document.querySelector(".logIn__password").value;
    let src = `/api/user/auth`
    logInData = {
        "email": email,
        "password": password
    };
    fetch(src, {
        method: "PUT",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify(logInData),
    }).then((response) => {
        return response.json();
    }).then(data => {
        let status = document.querySelector(".logIn__status");
        if (data.ok == true) {
            status.textContent = "登入成功"
            window.location.reload();
        };
        if (data.error == true) {
            status.textContent = data.message;
        }
    })
})


//會員註冊
let registerBtn = document.querySelector(".register__btn")
registerBtn.addEventListener('click', () => {
    let name = document.querySelector(".register__name").value
    let email = document.querySelector(".register__email").value
    let password = document.querySelector(".register__password").value
    let src = `/api/user`
    registerData = {
        "name": name,
        "email": email,
        "password": password
    };

    fetch(src, {
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify(registerData),
    }).then((response) => {
        return response.json();
    }).then(data => {
        let status = document.querySelector(".register__status");
        if (data.ok == true) {
            status.textContent = "註冊成功，請重新登入"
        }
        if (data.error == true) {
            status.textContent = data.message;
        }
    })
})
