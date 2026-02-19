document.addEventListener('DOMContentLoaded', () => {
    const uploadInput = document.getElementById('resume-upload');
    const fileNameDisplay = document.getElementById('file-name');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultsSection = document.getElementById('results-section');
    const loader = document.getElementById('loader');

    uploadInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = `Selected: ${e.target.files[0].name}`;
        }
    });

    analyzeBtn.addEventListener('click', async () => {
        const file = uploadInput.files[0];
        const jd = document.getElementById('job-description').value;

        if (!file) return alert('Please upload a resume first.');
        if (!jd) return alert('Please enter a job description.');

        // UI State
        loader.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        analyzeBtn.disabled = true;

        const formData = new FormData();
        formData.append('resume', file);
        formData.append('job_description', jd);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                displayResults(data);
            }
        } catch (error) {
            console.error(error);
            alert('Something went wrong. Please check if the backend is running.');
        } finally {
            loader.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });

    function displayResults(data) {
        resultsSection.classList.remove('hidden');

        // Score
        const scoreVal = document.getElementById('score-val');
        scoreVal.textContent = `${data.ats_analysis.score}%`;

        // Details
        document.getElementById('res-name').textContent = data.resume_data.name;
        document.getElementById('res-email').textContent = data.resume_data.email;
        document.getElementById('res-phone').textContent = data.resume_data.phone;

        // Skills
        const matchedContainer = document.getElementById('matched-skills');
        const missingContainer = document.getElementById('missing-skills');

        matchedContainer.innerHTML = data.ats_analysis.matched_skills.map(s => `<span>${s}</span>`).join('');
        missingContainer.innerHTML = data.ats_analysis.missing_skills.map(s => `<span>${s}</span>`).join('');

        // Smooth Scroll
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
});
