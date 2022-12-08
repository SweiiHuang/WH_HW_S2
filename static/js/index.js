let page = 0;
let keyword = "";
let currentLocation = window.location.origin
const src_categories = `/api/categories`
const showCategory = document.querySelector(".inputArea")
const spotInfo = document.getElementById("spotContainer");

//設定全域變數isLoading 來追蹤、記錄目前頁面是否正在載入 API，一開始設定為 false
let isLoading = false;
const observer = new IntersectionObserver((entries) => {
    if (entries[0].intersectionRatio > 0) {
        return fetchAttractions(page, keyword);
    }
});

observer.observe(document.querySelector("footer"));


//取得景點分類
function showCAT() {
    fetch(src_categories).then(function (response) {
        return response.json();
    }).then(function (data) {
        console.log(data);
        for (i = 0; i < data.data.length; i++) {
            let category = document.querySelector(".category")
            const categoryItem = document.createElement("div")
            categoryItem.className = "categoryItem"
            categoryItem.textContent = data.data[i]
            categoryItem.addEventListener("click", function () {
                let selectInput = document.querySelector(".inputArea");
                selectInput.value = this.textContent
                category.style.display = "none"
            });
            category.appendChild(categoryItem)
        }
    });
};
showCAT();

// 點擊顯示分類區塊
showCategory.addEventListener('click', function () {
    let revealCAT = document.querySelector(".category")
    revealCAT.style.display = "grid";
})

// 點選畫面隱藏分類區塊
document.addEventListener("click", function () {
    let hideCAT = document.querySelector(".category")
    hideCAT.style.display = "none";
}, true)

// 取得關鍵字搜尋
let search = document.querySelector(".searchBtn")
search.addEventListener("click", (e) => {
    // console.log('e', e);
    searchAttractions();
});


async function searchAttractions() {
    page = 0
    keyword = document.querySelector(".inputArea").value;
    src = `/api/attractions?page=${page}&keyword=${keyword}`;

    spotInfo.innerHTML = "";

    console.log('searchAttractions', isLoading);

    if (isLoading == false) {
        isLoading = true; //使用 fetch() 之前，將 isLoading 設定為 true，表示現在開始要呼叫 API 了

        const response = await fetch(src);
        const parsedData = await response.json();
        displayAttractions(parsedData)
    }
}


// 抓取景點資料
function fetchAttractions(page, keyword) {
    // keyword = document.querySelector(".inputArea").value;
    src = `/api/attractions?page=${page}&keyword=${keyword}`;

    console.log('fetchAttractions', isLoading)


    if (isLoading == false) {
        isLoading = true; //使用 fetch() 之前，將 isLoading 設定為 true，表示現在開始要呼叫 API 了

        fetch(src).then((response) => {
            return response.json();
        }).then(displayAttractions);
    }
}

//呈現景點畫面
function displayAttractions(data) {
    let attractionsData = data["data"];
    if (attractionsData.length == 0) {
        spotInfo.textContent = "無資料，請重新查詢"
    } else {
        for (i = 0; i < attractionsData.length; i++) {
            let id = attractionsData[i]["id"]
            let name = attractionsData[i]["name"]
            let category = attractionsData[i]["category"]
            let mrt = attractionsData[i]["mrt"]
            let images = attractionsData[i]["images"]
            let href_singleAttraction = `${currentLocation}/attraction/${id}`

            // 景點容器
            let singleAttractionPage = document.createElement("a");
            singleAttractionPage.setAttribute("href", href_singleAttraction)
            let newSpotBox = document.createElement("div");
            newSpotBox.className = "spotBox";
            singleAttractionPage.appendChild(newSpotBox)
            spotInfo.appendChild(singleAttractionPage);

            // 圖片
            let newImg = document.querySelector(".spotBox");
            let photo = document.createElement("img");
            photo.className = "spotImg";
            photo.src = images[0];
            newSpotBox.appendChild(photo);

            // 景點名稱背景
            let newTextBg = document.querySelector(".spotBox");
            let textBg = document.createElement("div");
            textBg.className = "spotOpacity";
            newSpotBox.appendChild(textBg);

            // 景點名稱
            let newSpotTitle = document.querySelector(".spotOpacity");
            let spotTile = document.createElement("div");
            spotTile.className = "spotTitle";
            spotTile.textContent = name;
            textBg.appendChild(spotTile);

            // 文字容器
            let newSpotMC = document.querySelector(".spotBox");
            let spotMrtCat = document.createElement("div");
            spotMrtCat.className = "spotMrtCat";
            newSpotBox.appendChild(spotMrtCat);

            // 捷運站
            let newMrt = document.querySelector(".spotMrtCat");
            let newSpotMrt = document.createElement("div");
            newSpotMrt.className = "spotMrt";
            newSpotMrt.textContent = mrt;
            spotMrtCat.appendChild(newSpotMrt);

            // 景點分類
            let newCat = document.querySelector(".spotMrtCat");
            let newSpotCat = document.createElement("div");
            newSpotCat.className = "spotCat";
            newSpotCat.textContent = category;
            spotMrtCat.appendChild(newSpotCat);
        }
    }
    if (data["nextPage"] === null) {
        observer.unobserve(document.querySelector("footer"));
    } else {
        page = data["nextPage"];
    }

    isLoading = false;
    // fetch() 載入完畢，取得後端回應後，將 isLoading 設定為 false，表示現在沒有在載入 API 了
}



