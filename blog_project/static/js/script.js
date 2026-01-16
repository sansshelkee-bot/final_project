// Main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this?')) {
                e.preventDefault();
            }
        });
    });

    // Markdown preview (if any)
    const markdownInput = document.getElementById('id_content');
    const markdownPreview = document.getElementById('markdown-preview');
    
    if (markdownInput && markdownPreview) {
        markdownInput.addEventListener('input', function() {
            // Simple markdown preview (you can use a library like marked.js)
            markdownPreview.innerHTML = marked.parse(this.value);
        });
    }
});