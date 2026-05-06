// Global variables
const API_BASE_URL = 'http://localhost:8000';
let currentAssessmentId = null;
let currentCandidateId = null;
let questions = [];
let currentQuestionIndex = 0;
let answers = [];

// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load admin stats if admin tab is selected
    if (tabName === 'admin') {
        loadAdminStats();
    }
}

// Start Assessment
document.getElementById('start-assessment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const candidateId = document.getElementById('candidate-id').value.trim();
    
    if (!candidateId) {
        alert('Please enter your Candidate ID');
        return;
    }
    
    try {
        // Create assessment
        const assessmentResponse = await fetch(`${API_BASE_URL}/assessments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                candidate_id: candidateId,
                domain: 'General Knowledge'
            })
        });
        
        if (!assessmentResponse.ok) throw new Error('Failed to create assessment');
        
        const assessment = await assessmentResponse.json();
        currentAssessmentId = assessment.id;
        currentCandidateId = candidateId;
        
        // Get questions (using existing assessment with questions)
        const questionsResponse = await fetch(`${API_BASE_URL}/assessments/1/questions`);
        
        if (!questionsResponse.ok) throw new Error('Failed to load questions');
        
        questions = await questionsResponse.json();
        
        if (questions.length === 0) {
            alert('No questions available. Please contact administrator.');
            return;
        }
        
        // Show questions section
        document.getElementById('questions-section').style.display = 'block';
        document.getElementById('start-assessment-form').style.display = 'none';
        
        // Load first question
        loadQuestion(0);
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error starting assessment. Please try again.');
    }
});

// Load question
function loadQuestion(index) {
    if (index >= questions.length) {
        completeAssessment();
        return;
    }
    
    currentQuestionIndex = index;
    const question = questions[index];
    
    // Update counter
    document.getElementById('question-counter').textContent = 
        `Question ${index + 1} of ${questions.length}`;
    
    // Display question
    document.getElementById('current-question').innerHTML = `
        <h3>Question ${index + 1}</h3>
        <p style="font-size: 1.1em; color: #333; margin-top: 10px;">${question.question_text}</p>
        <div class="question-meta">
            <span class="badge badge-difficulty">${question.difficulty}</span>
            <span class="badge badge-score">Max Score: ${question.max_score}</span>
        </div>
    `;
    
    // Clear answer text
    document.getElementById('answer-text').value = '';
    document.getElementById('char-count').textContent = '0';
    
    // Hide evaluation result
    document.getElementById('evaluation-result').style.display = 'none';
    document.getElementById('next-btn').style.display = 'none';
}

// Character counter
document.getElementById('answer-text').addEventListener('input', (e) => {
    document.getElementById('char-count').textContent = e.target.value.length;
});

// Submit answer
async function submitAnswer() {
    const answerText = document.getElementById('answer-text').value.trim();
    
    if (!answerText) {
        alert('Please enter your answer');
        return;
    }
    
    if (answerText.length < 20) {
        alert('Answer is too short. Please provide a more detailed answer (at least 20 characters).');
        return;
    }
    
    const question = questions[currentQuestionIndex];
    
    try {
        // Submit answer
        const answerResponse = await fetch(`${API_BASE_URL}/answers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                assessment_id: currentAssessmentId,
                question_id: question.id,
                candidate_id: currentCandidateId,
                answer_text: answerText
            })
        });
        
        if (!answerResponse.ok) throw new Error('Failed to submit answer');
        
        const answer = await answerResponse.json();
        
        // Evaluate answer
        const evaluationResponse = await fetch(`${API_BASE_URL}/evaluate/${answer.id}`, {
            method: 'POST'
        });
        
        if (!evaluationResponse.ok) throw new Error('Failed to evaluate answer');
        
        const evaluation = await evaluationResponse.json();
        
        // Store answer
        answers.push({
            question: question.question_text,
            answer: answerText,
            evaluation: evaluation
        });
        
        // Display evaluation
        displayEvaluation(evaluation);
        
        // Show next button
        document.getElementById('next-btn').style.display = 'inline-block';
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error submitting answer. Please try again.');
    }
}

// Display evaluation
function displayEvaluation(evaluation) {
    const resultDiv = document.getElementById('evaluation-result');
    
    const percentage = evaluation.percentage;
    let performanceClass = 'poor';
    if (percentage >= 80) performanceClass = 'excellent';
    else if (percentage >= 60) performanceClass = 'good';
    else if (percentage >= 40) performanceClass = 'average';
    
    resultDiv.innerHTML = `
        <h3>✅ Answer Evaluated!</h3>
        
        <div class="score-grid">
            <div class="score-item">
                <h4>Correctness</h4>
                <div class="score-value">${evaluation.metric_scores.correctness_score}/10</div>
            </div>
            <div class="score-item">
                <h4>Depth</h4>
                <div class="score-value">${evaluation.metric_scores.depth_score}/10</div>
            </div>
            <div class="score-item">
                <h4>Clarity</h4>
                <div class="score-value">${evaluation.metric_scores.clarity_score}/10</div>
            </div>
            <div class="score-item">
                <h4>Final Score</h4>
                <div class="score-value">${evaluation.final_score}/${evaluation.max_score}</div>
            </div>
        </div>
        
        ${evaluation.negative_marking.negative_marks > 0 ? `
            <div class="feedback-box" style="background: rgba(255, 0, 0, 0.2);">
                <strong>⚠️ Negative Marking:</strong> -${evaluation.negative_marking.negative_marks} marks<br>
                <small>${evaluation.negative_marking.negative_reason}</small>
            </div>
        ` : ''}
        
        <div class="feedback-box">
            <strong>📝 Feedback:</strong><br>
            ${evaluation.evaluation_feedback}
        </div>
        
        <div style="text-align: center; margin-top: 15px;">
            <span class="score-badge ${performanceClass}" style="font-size: 1.2em; padding: 10px 20px;">
                ${percentage.toFixed(1)}% - ${performanceClass.toUpperCase()}
            </span>
        </div>
    `;
    
    resultDiv.style.display = 'block';
}

// Next question
function nextQuestion() {
    loadQuestion(currentQuestionIndex + 1);
}

// Complete assessment
async function completeAssessment() {
    try {
        // Complete the assessment
        const response = await fetch(`${API_BASE_URL}/assessments/${currentAssessmentId}/complete`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Failed to complete assessment');
        
        const assessment = await response.json();
        
        // Show completion message
        document.getElementById('questions-section').innerHTML = `
            <div class="card">
                <div class="results-summary">
                    <h2>🎉 Assessment Completed!</h2>
                    <div class="summary-stats">
                        <div class="summary-stat">
                            <h3>Total Questions</h3>
                            <p>${assessment.total_questions}</p>
                        </div>
                        <div class="summary-stat">
                            <h3>Your Score</h3>
                            <p>${assessment.total_score.toFixed(2)}</p>
                        </div>
                        <div class="summary-stat">
                            <h3>Max Score</h3>
                            <p>${assessment.max_possible_score.toFixed(2)}</p>
                        </div>
                        <div class="summary-stat">
                            <h3>Percentage</h3>
                            <p>${assessment.percentage.toFixed(1)}%</p>
                        </div>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <p style="font-size: 1.1em; margin-bottom: 15px;">
                        Your Candidate ID: <strong>${currentCandidateId}</strong>
                    </p>
                    <button onclick="location.reload()" class="btn btn-primary">Take Another Assessment</button>
                    <button onclick="viewResults('${currentCandidateId}')" class="btn btn-secondary">View Detailed Results</button>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error completing assessment. Please try again.');
    }
}

// View results
document.getElementById('view-results-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const candidateId = document.getElementById('search-candidate-id').value.trim();
    viewResults(candidateId);
});

async function viewResults(candidateId) {
    if (!candidateId) {
        alert('Please enter Candidate ID');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/reports/candidate/${candidateId}`);
        
        if (!response.ok) throw new Error('No results found');
        
        const report = await response.json();
        
        // Display results
        const resultsDiv = document.getElementById('results-display');
        
        let html = `
            <div class="card">
                <div class="results-summary">
                    <h2>📊 Results for ${report.candidate_id}</h2>
                    <div class="summary-stats">
                        <div class="summary-stat">
                            <h3>Total Assessments</h3>
                            <p>${report.total_assessments}</p>
                        </div>
                        <div class="summary-stat">
                            <h3>Questions Answered</h3>
                            <p>${report.total_questions_answered}</p>
                        </div>
                        <div class="summary-stat">
                            <h3>Average Score</h3>
                            <p>${report.average_score.toFixed(2)}</p>
                        </div>
                        <div class="summary-stat">
                            <h3>Highest Score</h3>
                            <p>${report.highest_score.toFixed(2)}</p>
                        </div>
                    </div>
                </div>
                
                <div class="answer-history">
                    <h3>Answer History</h3>
        `;
        
        report.score_history.forEach((item, index) => {
            const percentage = item.percentage;
            let performanceClass = 'poor';
            if (percentage >= 80) performanceClass = 'excellent';
            else if (percentage >= 60) performanceClass = 'good';
            else if (percentage >= 40) performanceClass = 'average';
            
            html += `
                <div class="answer-item">
                    <h4>${index + 1}. ${item.question_text}</h4>
                    <div class="answer-text">${item.answer_text}</div>
                    <div class="score-breakdown">
                        <span class="score-badge ${performanceClass}">
                            Score: ${item.final_score}/${item.max_score} (${percentage.toFixed(1)}%)
                        </span>
                        <span style="color: #666; font-size: 0.9em;">
                            Submitted: ${new Date(item.submitted_at).toLocaleString()}
                        </span>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
        
        resultsDiv.innerHTML = html;
        resultsDiv.style.display = 'block';
        
        // Switch to results tab
        showTab('view-results');
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
        
    } catch (error) {
        console.error('Error:', error);
        alert('No results found for this Candidate ID.');
    }
}

// Load admin stats
async function loadAdminStats() {
    try {
        // This is a simplified version - you can enhance it with actual API calls
        const assessmentsResponse = await fetch(`${API_BASE_URL}/assessments/1`);
        const questionsResponse = await fetch(`${API_BASE_URL}/assessments/1/questions`);
        
        if (assessmentsResponse.ok) {
            const assessment = await assessmentsResponse.json();
            document.getElementById('total-assessments').textContent = '1+';
        }
        
        if (questionsResponse.ok) {
            const questions = await questionsResponse.json();
            document.getElementById('total-questions').textContent = questions.length;
        }
        
    } catch (error) {
        console.error('Error loading admin stats:', error);
    }
}

// View all questions
async function viewAllQuestions() {
    try {
        const response = await fetch(`${API_BASE_URL}/assessments/1/questions`);
        
        if (!response.ok) throw new Error('Failed to load questions');
        
        const questions = await response.json();
        
        let html = '<div class="card"><h3>All Questions</h3><div class="questions-list">';
        
        questions.forEach((q, index) => {
            html += `
                <div class="question-item">
                    <h4>${index + 1}. ${q.question_text}</h4>
                    <p>Difficulty: ${q.difficulty} | Max Score: ${q.max_score}</p>
                </div>
            `;
        });
        
        html += '</div></div>';
        
        document.getElementById('all-questions-display').innerHTML = html;
        document.getElementById('all-questions-display').style.display = 'block';
        
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load questions.');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Assessment System loaded');
});
