function toggleSQL(button) {
    const fullSQL = button.nextElementSibling;
    if (fullSQL.style.display === "none") {
        fullSQL.style.display = "block";
        button.textContent = "折りたたむ";
    } else {
        fullSQL.style.display = "none";
        button.textContent = "全文表示";
    }
}
