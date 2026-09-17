function countCharacters(textareaId, targetId) {
    const textarea = document.getElementById(textareaId);
    const target = document.getElementById(targetId);
    if (!textarea || !target) return;
    target.textContent = textarea.value.length;
    textarea.addEventListener('input', function () {
        target.textContent = textarea.value.length;
    });
}
