const app = document.getElementById("academics-app");

const LIST_URL = app.dataset.listUrl;
const CREATE_URL = app.dataset.createUrl;
const STAR_URL_TEMPLATE = app.dataset.starUrlTemplate;
const EDIT_URL_TEMPLATE = app.dataset.editUrlTemplate;
const DELETE_URL_TEMPLATE = app.dataset.deleteUrlTemplate;
const LOGIN_URL = app.dataset.loginUrl;

const CAN_MANAGE = app.dataset.canManage === "true";
const CAN_EDIT = app.dataset.canEdit === "true";
const IS_AUTHENTICATED =
    app.dataset.isAuthenticated === "true";

const loadingState =
    document.getElementById("academics-loading");

const errorState =
    document.getElementById("academics-error");

const emptyState =
    document.getElementById("academics-empty");

const listContainer =
    document.getElementById("academics-list");

const searchForm =
    document.getElementById("academic-search-form");

const searchInput =
    document.getElementById("academic-search-input");

const academicForm =
    document.getElementById("academic-form");


const SEARCH_DEBOUNCE_DELAY = 300;

let searchDebounceTimer = null;
let academicsAbortController = null;


function displayPageSection({
    showLoading = false,
    showError = false,
    showEmpty = false,
    showList = false,
}) {
    loadingState.classList.toggle(
        "hide",
        !showLoading
    );

    errorState.classList.toggle(
        "hide",
        !showError
    );

    emptyState.classList.toggle(
        "hide",
        !showEmpty
    );

    listContainer.classList.toggle(
        "hide",
        !showList
    );
}


function createAcademicUrl(template, academicId) {
    return template.replace(
        "00000000-0000-0000-0000-000000000000",
        academicId
    );
}


function buildAcademicCard(item) {
    const academic = item.fields;
    const academicId = item.pk;

    const article = document.createElement("article");
    article.className = "academic-item";


    const level = document.createElement("span");
    level.className = "academic-level";
    level.textContent = academic.level_display;


    const institution = document.createElement("h2");
    institution.textContent = academic.institution;


    const period = document.createElement("p");
    period.className = "academic-period";
    period.textContent = academic.period;


    const actions = document.createElement("div");
    actions.className = "project-actions";


    // =========================
    // STAR
    // =========================

    if (IS_AUTHENTICATED) {

        const starForm = document.createElement("form");
        starForm.method = "post";
        starForm.className = "star-form";

        starForm.action =
            createAcademicUrl(
                STAR_URL_TEMPLATE,
                academicId
            );


        const starButton =
            document.createElement("button");

        starButton.type = "submit";

        starButton.className =
            "button button-star";

        if (academic.is_starred) {
            starButton.classList.add("is-starred");
        }


        const starIcon =
            document.createElement("span");

        starIcon.setAttribute(
            "aria-hidden",
            "true"
        );

        starIcon.textContent = "★";


        const starCount =
            document.createElement("span");

        starCount.className = "star-count";
        starCount.textContent =
            academic.star_count;


        starButton.append(
            starIcon,
            document.createTextNode(
                academic.is_starred
                    ? "Unstar"
                    : "Star"
            ),
            starCount
        );


        starForm.appendChild(starButton);


        starForm.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();

                try {

                    const response = await fetch(
                        starForm.action,
                        {
                            method: "POST",
                            headers: {
                                "X-CSRFToken":
                                    getCookie("csrftoken"),

                                "X-Requested-With":
                                    "XMLHttpRequest",

                                "Accept":
                                    "application/json",
                            },
                        }
                    );


                    if (!response.ok) {
                        throw new Error(
                            "Gagal mengubah star."
                        );
                    }


                    const result =
                        await response.json();


                    academic.is_starred =
                        result.is_starred;

                    academic.star_count =
                        result.star_count;


                    starButton.classList.toggle(
                        "is-starred",
                        result.is_starred
                    );


                    starButton.replaceChildren(
                        starIcon,
                        document.createTextNode(
                            result.is_starred
                                ? "Unstar"
                                : "Star"
                        ),
                        starCount
                    );


                    starCount.textContent =
                        result.star_count;

                } catch (error) {

                    console.error(
                        error
                    );

                    showToast(
                        "Gagal",
                        "Tidak dapat mengubah star.",
                        "error"
                    );
                }
            }
        );


        actions.appendChild(starForm);

    } else {

        const loginLink =
            document.createElement("a");

        loginLink.className =
            "button button-star";

        loginLink.href =
            `${LOGIN_URL}?next=${encodeURIComponent(
                window.location.pathname +
                window.location.search
            )}`;

        loginLink.textContent =
            "★ Login untuk star ";

        const starCount =
            document.createElement("span");

        starCount.className = "star-count";
        starCount.textContent =
            academic.star_count;

        loginLink.appendChild(starCount);

        actions.appendChild(loginLink);
    }


    // =========================
    // EDIT
    // =========================

    if (CAN_EDIT) {

        const editLink =
            document.createElement("a");

        editLink.className =
            "button button-secondary";

        editLink.href =
            createAcademicUrl(
                EDIT_URL_TEMPLATE,
                academicId
            );

        editLink.textContent = "Edit";

        actions.appendChild(editLink);
    }


    // =========================
    // DELETE
    // =========================

    if (CAN_MANAGE) {

        const deleteForm =
            document.createElement("form");

        deleteForm.method = "post";

        deleteForm.action =
            createAcademicUrl(
                DELETE_URL_TEMPLATE,
                academicId
            );


        const csrfInput =
            document.createElement("input");

        csrfInput.type = "hidden";
        csrfInput.name =
            "csrfmiddlewaretoken";

        csrfInput.value =
            getCookie("csrftoken");


        const deleteButton =
            document.createElement("button");

        deleteButton.type = "submit";

        deleteButton.className =
            "button button-danger";

        deleteButton.textContent =
            "Hapus";


        deleteForm.addEventListener(
            "submit",
            function (event) {

                const confirmed = confirm(
                    `Hapus riwayat ${academic.institution}?`
                );

                if (!confirmed) {
                    event.preventDefault();
                }
            }
        );


        deleteForm.append(
            csrfInput,
            deleteButton
        );

        actions.appendChild(deleteForm);
    }


    article.append(
        level,
        institution,
        period,
        actions
    );

    return article;
}


async function fetchAcademics(query = "") {

    if (academicsAbortController) {
        academicsAbortController.abort();
    }

    academicsAbortController =
        new AbortController();


    displayPageSection({
        showLoading: true,
    });


    try {

        const url = query
            ? `${LIST_URL}?q=${encodeURIComponent(query)}`
            : LIST_URL;


        const response = await fetch(
            url,
            {
                headers: {
                    "Accept":
                        "application/json",
                },

                signal:
                    academicsAbortController.signal,
            }
        );


        if (!response.ok) {
            throw new Error(
                "Gagal mengambil data."
            );
        }


        const data =
            await response.json();


        listContainer.replaceChildren();


        if (data.length === 0) {

            displayPageSection({
                showEmpty: true,
            });

            return;
        }


        data.forEach(function (item) {

            listContainer.appendChild(
                buildAcademicCard(item)
            );

        });


        displayPageSection({
            showList: true,
        });

    } catch (error) {

        if (error.name === "AbortError") {
            return;
        }

        console.error(error);

        displayPageSection({
            showError: true,
        });
    }
}


// =========================
// SEARCH
// =========================

searchInput.addEventListener(
    "input",
    function () {

        clearTimeout(
            searchDebounceTimer
        );

        searchDebounceTimer =
            setTimeout(
                function () {

                    fetchAcademics(
                        searchInput.value.trim()
                    );

                },
                SEARCH_DEBOUNCE_DELAY
            );
    }
);


searchForm.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();

        clearTimeout(
            searchDebounceTimer
        );

        fetchAcademics(
            searchInput.value.trim()
        );
    }
);


// =========================
// ADD ACADEMIC
// =========================

if (academicForm) {

    academicForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const submitButton =
                academicForm.querySelector(
                    'button[type="submit"]'
                );

            submitButton.disabled = true;


            document
                .querySelectorAll(".field-error")
                .forEach(function (element) {
                    element.textContent = "";
                });


            try {

                const response =
                    await fetch(
                        CREATE_URL,
                        {
                            method: "POST",

                            headers: {
                                "X-CSRFToken":
                                    getCookie("csrftoken"),

                                "X-Requested-With":
                                    "XMLHttpRequest",

                                "Accept":
                                    "application/json",
                            },

                            body:
                                new FormData(
                                    academicForm
                                ),
                        }
                    );


                const result =
                    await response.json()
                        .catch(() => ({}));


                if (response.status === 201) {

                    academicForm.reset();


                    const modal =
                        document.getElementById(
                            "add-academic-modal"
                        );

                    modal.hidePopover();


                    showToast(
                        "Berhasil",
                        "Riwayat akademik berhasil ditambahkan.",
                        "success"
                    );


                    fetchAcademics(
                        searchInput.value.trim()
                    );

                    return;
                }


                if (response.status === 400) {

                    if (result.errors) {

                        Object.entries(
                            result.errors
                        ).forEach(
                            function ([fieldName, errors]) {

                                const errorElement =
                                    document.querySelector(
                                        `[data-error-for="${fieldName}"]`
                                    );

                                if (!errorElement) {
                                    return;
                                }

                                errorElement.textContent =
                                    errors
                                        .map(
                                            error =>
                                                error.message
                                        )
                                        .join(" ");

                            }
                        );
                    }


                    const messages =
                        result.errors
                            ? Object.values(
                                result.errors
                            )
                                .flat()
                                .map(
                                    error =>
                                        error.message
                                )
                            : [
                                "Data tidak valid."
                            ];


                    showToast(
                        "Gagal",
                        messages.join(" "),
                        "error"
                    );

                    return;
                }


                showToast(
                    "Gagal",
                    result.message ||
                        `Terjadi kesalahan (${response.status}).`,
                    "error"
                );

            } catch (error) {

                console.error(error);

                showToast(
                    "Gagal",
                    "Tidak dapat terhubung ke server.",
                    "error"
                );

            } finally {

                submitButton.disabled = false;
            }
        }
    );
}


// =========================
// START
// =========================

fetchAcademics(
    searchInput.value.trim()
);