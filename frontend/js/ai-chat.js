async sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    this.addMessage(message, 'user');
    input.value = '';
    
    this.showTypingIndicator();
    
    try {
        // Use the correct API method
        const response = await window.api.askAIQuestion(message);
        
        this.removeTypingIndicator();
        this.addMessage(response.answer, 'ai');
        
    } catch (error) {
        this.removeTypingIndicator();
        this.addMessage('Sorry, I encountered an error. Please ensure you have uploaded a file first.', 'ai');
        console.error('AI chat error:', error);
    }
}