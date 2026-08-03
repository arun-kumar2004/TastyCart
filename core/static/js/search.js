/*=====================================================
            TastyCart Common Search
=====================================================*/

const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");

let typingTimer = null;

function debounce(callback, delay = 350) {

    clearTimeout(typingTimer);

    typingTimer = setTimeout(callback, delay);

}

function isMenuPage() {

    return window.location.pathname.includes("/menu/");

}

function isHomePage() {

    return window.location.pathname === "/";

}

function getSearchKeyword() {

    return searchInput.value.trim();

}

function redirectToMenu(keyword) {

    if (!keyword) return;

    window.location.href =
        `/menu/menu/?search=${encodeURIComponent(keyword)}`;

}

/*=====================================================
                AJAX SEARCH
=====================================================*/

async function searchItems(keyword) {

    if (!keyword) return;

    // Home Page
    if (isHomePage()) {

        redirectToMenu(keyword);

        return;
    }

    // Menu Page
    try {

        const response = await fetch(
            `/menu/search/?q=${encodeURIComponent(keyword)}`
        );

        const data = await response.json();

        showSearchResult(data, keyword);

    } catch (error) {

        console.error("Search Error :", error);

    }

}

/*=====================================================
            INPUT EVENTS
=====================================================*/

if (searchInput) {

    searchInput.addEventListener("keyup", function () {

        const keyword = getSearchKeyword();

        debounce(() => {

           setTimeout(()=>{

    searchItems(keyword);

},500);

        });

    });

}

if (searchBtn) {

    searchBtn.addEventListener("click", function () {

        searchItems(getSearchKeyword());

    });

}

/*=====================================================
      AUTO SEARCH WHEN PAGE LOADS
=====================================================*/

document.addEventListener("DOMContentLoaded", () => {

    if (!isMenuPage()) return;

    const params = new URLSearchParams(window.location.search);

    const keyword = params.get("search");

    if (!keyword) return;

    if (searchInput) {

        searchInput.value = keyword;

    }

   setTimeout(()=>{

    searchItems(keyword);

},500);

});

/*=====================================================
        SHOW SEARCH RESULT
=====================================================*/

function showSearchResult(results, keyword) {

    if(!Array.isArray(results) || results.length===0){

        alert("No item found.");

        return;

    }

    const item = results[0];

    // open category
    openCategory(item.category);

    // wait for DOM update
    setTimeout(() => {

        goToItem(item.id);

    }, 250);

}

/*=====================================================
        OPEN CATEGORY
=====================================================*/

function openCategory(categoryId) {

    // Tabs
    document.querySelectorAll(".tab-btn").forEach(btn => {

        btn.classList.remove("active");

    });

    const activeTab = document.querySelector(
        `.tab-btn[data-tab="${categoryId}"]`
    );

    if (activeTab)
        activeTab.classList.add("active");

    // Sections
    document.querySelectorAll(".category-section")
    .forEach(section => {

        section.classList.add("hidden");

    });

    const activeSection =
        document.getElementById("tab" + categoryId);

    if (activeSection)
        activeSection.classList.remove("hidden");

}

/*=====================================================
        FIND ITEM
=====================================================*/
function goToItem(itemId){

    const activeSection = document.querySelector(".category-section:not(.hidden)");

    if(!activeSection)
        return;

    const cards = activeSection.querySelectorAll(".item-card");

    let index = -1;

    cards.forEach((card, i) => {

        if(Number(card.dataset.id) === Number(itemId))
            index = i;

    });

    if(index === -1)
        return;

    highlightItem(itemId);

}

/*=====================================================
            HIGHLIGHT ITEM
=====================================================*/
function highlightItem(itemId){

    // Remove previous highlight
    document.querySelectorAll(".item-card").forEach(card => {

        card.classList.remove(
            "ring-4",
            "ring-red-500",
            "shadow-2xl",
            "scale-105"
        );

    });

    // Find item
    const card = document.querySelector(
        `.item-card[data-id="${itemId}"]`
    );

    if(!card)
        return;

    // Highlight
    card.classList.add(
        "ring-4",
        "ring-red-500",
        "shadow-2xl",
        "scale-105"
    );

    // Scroll to item
    card.scrollIntoView({

        behavior: "smooth",

        block: "center"

    });

    // Remove highlight after 4 sec
    setTimeout(() => {

        card.classList.remove(
            "ring-4",
            "ring-red-500",
            "shadow-2xl",
            "scale-105"
        );

    }, 4000);

}