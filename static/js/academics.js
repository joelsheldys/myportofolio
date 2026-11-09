const app = document.getElementById("academics-app");

const LIST_URL = app.dataset.listUrl;
const DETAIL_URL_TEMPLATE = app.dataset.detailUrlTemplate;
const STAR_URL_TEMPLATE = app.dataset.starUrlTemplate;
const LOGIN_URL = app.dataset.loginUrl;
const CAN_MANAGE = app.dataset.canManage === "true";
const CAN_EDIT = app.dataset.canEdit === "true";
const IS_AUTHENTICATED = app.dataset.isAuthenticated === "true";

const loadingState = document.getElementById("academics-loading");
const errorState = document.getElementById("academics-error");
const emptyState = document.getElementById("academics-empty");
const listContainer = document.getElementById("academics-list");
const searchForm = document.getElementById("academic-search-form");
const searchInput = document.getElementById("academic-search-input");
const academicForm = document.getElementById("academic-form");
const formModal = document.getElementById("academic-form-modal");
const formTitle = document.getElementById("academic-form-modal-title");
const formSubmit = document.getElementById("academic-form-submit");
const formGeneralError = document.getElementById("academic-form-general-error");
const deleteModal = document.getElementById("academic-delete-modal");
const deleteName = document.getElementById("academic-delete-name");
const deleteConfirm = document.getElementById("academic-delete-confirm");

const SEARCH_DEBOUNCE_DELAY = 300;
const UUID_PLACEHOLDER = "00000000-0000-0000-0000-000000000000";

let searchDebounceTimer = null;
let academicsAbortController = null;
let formAcademic = null;
let academicToDelete = null;

async function apiRequest(url, { method = "GET", body, signal } = {}) {
    const headers = { Accept: "application/json" };
    if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
        headers["X-CSRFToken"] = getCookie("csrftoken") || "";
    }
    if (body !== undefined) headers["Content-Type"] = "application/json";
    const response = await fetch(url, {
        method,
        headers,
        signal,
        credentials: "same-origin",
        body: body === undefined ? undefined : JSON.stringify(body),
    });
    const data = response.status === 204 ? null : await response.json().catch(() => null);
    return { response, data };
}

function displayPageSection({
    showLoading = false,
    showError = false,
    showEmpty = false,
    showList = false,
}) {
    loadingState.classList.toggle("hide", !showLoading);
    errorState.classList.toggle("hide", !showError);
    emptyState.classList.toggle("hide", !showEmpty);
    listContainer.classList.toggle("hide", !showList);
}

function createAcademicUrl(template, academicId) {
    return template.replace(UUID_PLACEHOLDER, academicId);
}

function buildAcademicCard(academic) {
    const article = document.createElement("article");
    article.className = "academic-item";
    article.dataset.academicId = academic.id;

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

    if (IS_AUTHENTICATED) {
        const starButton = document.createElement("button");
        starButton.type = "button";
        starButton.className = "button button-star";
        starButton.classList.toggle("is-starred", academic.is_starred);
        starButton.append(
            document.createTextNode(academic.is_starred ? "Unstar " : "Star "),
        );

        const starCount = document.createElement("span");
        starCount.className = "star-count";
        starCount.textContent = String(academic.star_count);
        starButton.appendChild(starCount);
        starButton.addEventListener("click", () => toggleStar(article, academic));
        actions.appendChild(starButton);
    } else {
        const loginLink = document.createElement("a");
        const next = window.location.pathname + window.location.search;
        const loginQuery = new URLSearchParams({ next });
        loginLink.className = "button button-star";
        loginLink.href = `${LOGIN_URL}?${loginQuery.toString()}`;
        loginLink.textContent = "★ Login untuk star ";

        const starCount = document.createElement("span");
        starCount.className = "star-count";
        starCount.textContent = String(academic.star_count);
        loginLink.appendChild(starCount);
        actions.appendChild(loginLink);
    }

    if (CAN_EDIT) {
        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.className = "button button-secondary";
        editButton.textContent = "Edit";
        editButton.addEventListener("click", () => openFormModal(academic));
        actions.appendChild(editButton);
    }

    if (CAN_MANAGE) {
        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "button button-danger";
        deleteButton.textContent = "Hapus";
        deleteButton.addEventListener("click", () => openDeleteModal(academic));
        actions.appendChild(deleteButton);
    }

    article.append(level, institution, period, actions);
    return article;
}

function parseApiError(data, status) {
    const fieldErrors = {};
    const generalMessages = [];

    if (data && typeof data === "object" && !Array.isArray(data)) {
        for (const [field, value] of Object.entries(data)) {
            const values = Array.isArray(value) ? value : [value];
            const message = values
                .filter((item) => typeof item === "string")
                .join(" ");
            if (!message) continue;

            if (field === "detail" || field === "non_field_errors") {
                generalMessages.push(message);
            } else {
                fieldErrors[field] = message;
            }
        }
    }

    const message = [
        ...Object.values(fieldErrors),
        ...generalMessages,
    ].join(" ") || `Permintaan gagal (HTTP ${status}).`;

    return {
        fieldErrors,
        generalMessage: generalMessages.join(" "),
        message,
    };
}

function toastApiError(response, data) {
    const titles = {
        400: "Data tidak valid",
        403: "Akses ditolak",
        404: "Data tidak ditemukan",
    };
    const parsedError = parseApiError(data, response.status);
    showToast(
        titles[response.status] || "Permintaan gagal",
        parsedError.message,
        "error",
    );
    return parsedError;
}

function showNetworkError() {
    showToast("Gagal", "Tidak dapat terhubung ke server.", "error");
}

function clearFormErrors() {
    formGeneralError.textContent = "";
    academicForm.querySelectorAll("[data-error-for]").forEach((errorElement) => {
        errorElement.textContent = "";
    });
}

function displayFormErrors(parsedError) {
    clearFormErrors();
    formGeneralError.textContent = parsedError.generalMessage;

    for (const [field, message] of Object.entries(parsedError.fieldErrors)) {
        const errorElement = academicForm.querySelector(
            `[data-error-for="${CSS.escape(field)}"]`,
        );
        if (errorElement) errorElement.textContent = message;
    }
}

async function fetchAcademics(query = "", { silent = false } = {}) {
    if (academicsAbortController) academicsAbortController.abort();

    const controller = new AbortController();
    academicsAbortController = controller;
    if (!silent) displayPageSection({ showLoading: true });

    const url = new URL(LIST_URL, document.baseURI);
    url.searchParams.set("q", query);

    try {
        const { response, data } = await apiRequest(url, { signal: controller.signal });
        if (controller !== academicsAbortController) return;

        if (!response.ok) {
            toastApiError(response, data);
            displayPageSection({ showError: true });
            return;
        }

        listContainer.replaceChildren();
        if (data.length === 0) {
            displayPageSection({ showEmpty: true });
            return;
        }

        data.forEach((academic) => {
            listContainer.appendChild(buildAcademicCard(academic));
        });
        displayPageSection({ showList: true });
    } catch (error) {
        if (error.name === "AbortError") return;
        if (controller !== academicsAbortController) return;
        console.error(error);
        displayPageSection({ showError: true });
        showNetworkError();
    }
}

async function toggleStar(card, academic) {
    try {
        const url = createAcademicUrl(STAR_URL_TEMPLATE, academic.id);
        const { response, data } = await apiRequest(url, { method: "POST" });
        if (!response.ok) {
            toastApiError(response, data);
            return;
        }
        card.replaceWith(buildAcademicCard(data));
    } catch (error) {
        console.error(error);
        showNetworkError();
    }
}

function setAcademicFormValue(name, value) {
    const field = academicForm.elements.namedItem(name);
    if (field) field.value = value === null || value === undefined ? "" : String(value);
}

function openFormModal(academic = null) {
    if (!academicForm || !formModal) return;

    formAcademic = academic;
    academicForm.reset();
    clearFormErrors();

    if (academic) {
        formTitle.textContent = "Ubah Riwayat Akademik";
        formSubmit.textContent = "Simpan Perubahan";
        setAcademicFormValue("institution", academic.institution);
        setAcademicFormValue("level", academic.level);
        setAcademicFormValue("start_year", academic.start_year);
        setAcademicFormValue("end_year", academic.end_year);
    } else {
        formTitle.textContent = "Tambah Riwayat Akademik";
        formSubmit.textContent = "Tambah Riwayat";
    }

    formModal.showPopover();
}

async function submitAcademicForm(event) {
    event.preventDefault();
    clearFormErrors();

    const formData = new FormData(academicForm);
    const endYear = formData.get("end_year");
    const body = {
        institution: formData.get("institution"),
        level: formData.get("level"),
        start_year: Number(formData.get("start_year")),
        end_year: endYear === "" ? null : Number(endYear),
    };
    const url = formAcademic
        ? createAcademicUrl(DETAIL_URL_TEMPLATE, formAcademic.id)
        : LIST_URL;
    const method = formAcademic ? "PATCH" : "POST";

    formSubmit.disabled = true;
    try {
        const { response, data } = await apiRequest(url, { method, body });
        if (!response.ok) {
            const parsedError = toastApiError(response, data);
            if (response.status === 400) displayFormErrors(parsedError);
            return;
        }

        formModal.hidePopover();
        showToast(
            "Berhasil",
            formAcademic
                ? "Riwayat akademik berhasil diperbarui."
                : "Riwayat akademik berhasil ditambahkan.",
            "success",
        );
        await fetchAcademics(searchInput.value.trim(), { silent: true });
    } catch (error) {
        console.error(error);
        showNetworkError();
    } finally {
        formSubmit.disabled = false;
    }
}

function openDeleteModal(academic) {
    if (!deleteModal) return;
    academicToDelete = academic;
    deleteName.textContent = academic.institution;
    deleteModal.showPopover();
}

async function confirmDelete() {
    if (!academicToDelete) return;

    deleteConfirm.disabled = true;
    try {
        const url = createAcademicUrl(DETAIL_URL_TEMPLATE, academicToDelete.id);
        const { response, data } = await apiRequest(url, { method: "DELETE" });
        if (response.status !== 204) {
            toastApiError(response, data);
            return;
        }

        deleteModal.hidePopover();
        academicToDelete = null;
        showToast("Berhasil", "Riwayat akademik berhasil dihapus.", "success");
        await fetchAcademics(searchInput.value.trim(), { silent: true });
    } catch (error) {
        console.error(error);
        showNetworkError();
    } finally {
        deleteConfirm.disabled = false;
    }
}

document.getElementById("academic-add-button")?.addEventListener("click", () => {
    openFormModal();
});

document.querySelectorAll("[data-close-academic-form]").forEach((button) => {
    button.addEventListener("click", () => formModal.hidePopover());
});

document.querySelectorAll("[data-close-academic-delete]").forEach((button) => {
    button.addEventListener("click", () => {
        deleteModal.hidePopover();
        academicToDelete = null;
    });
});

if (academicForm) academicForm.addEventListener("submit", submitAcademicForm);
if (deleteConfirm) deleteConfirm.addEventListener("click", confirmDelete);

searchInput.addEventListener("input", () => {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
        fetchAcademics(searchInput.value.trim());
    }, SEARCH_DEBOUNCE_DELAY);
});

searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    clearTimeout(searchDebounceTimer);
    fetchAcademics(searchInput.value.trim());
});

fetchAcademics(searchInput.value.trim());
