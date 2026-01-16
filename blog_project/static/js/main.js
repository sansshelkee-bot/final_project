// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // ============================================
    // EXISTING CODE
    // ============================================
    
    // Mobile Menu Toggle
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
    
    // Close Messages
    document.querySelectorAll('.close-btn').forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });
    
    // Auto-hide messages after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        });
    }, 5000);
    
    // Search functionality
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="q"]');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }
    
    // Like buttons
    document.querySelectorAll('.btn-like').forEach(button => {
        button.addEventListener('click', async function() {
            const postId = this.dataset.postId;
            const likeCount = this.querySelector('.like-count');
            
            try {
                const response = await fetch(`/api/posts/${postId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    likeCount.textContent = data.likes_count;
                    this.classList.toggle('liked', data.liked);
                    
                    // Track like for KNN recommendations
                    if (window.blogRecommender) {
                        window.blogRecommender.trackInteraction(postId, 'like');
                    }
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });
    
    // Comment reply system
    document.querySelectorAll('.btn-reply').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            const replyForm = document.querySelector('.comment-form');
            
            if (replyForm) {
                const parentInput = replyForm.querySelector('input[name="parent_id"]');
                const textarea = replyForm.querySelector('textarea');
                
                parentInput.value = commentId;
                textarea.focus();
                textarea.placeholder = 'Replying to comment...';
                
                // Scroll to form
                replyForm.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
    
    // ============================================
    // KNN RECOMMENDATION SYSTEM
    // ============================================
    
    class BlogKNNRecommender {
        constructor() {
            this.k = 5;
            this.distanceMetric = 'cosine';
            this.items = new Map();
            this.userHistory = this.loadUserHistory();
            this.recommendationCache = new Map();
            this.cacheTTL = 300000; // 5 minutes
            this.initialized = false;
        }
        
        loadUserHistory() {
            try {
                const history = localStorage.getItem('blog_user_history');
                return history ? JSON.parse(history) : [];
            } catch {
                return [];
            }
        }
        
        saveUserHistory() {
            try {
                localStorage.setItem('blog_user_history', JSON.stringify(this.userHistory));
            } catch (error) {
                console.warn('Could not save user history:', error);
            }
        }
        
        addToHistory(postId, postTitle, postCategory, postUrl) {
            // Remove if already exists
            this.userHistory = this.userHistory.filter(item => item.id !== postId);
            
            // Add to beginning
            this.userHistory.unshift({
                id: postId,
                title: postTitle,
                category: postCategory,
                url: postUrl || window.location.href,
                timestamp: Date.now()
            });
            
            // Keep only last 20 items
            if (this.userHistory.length > 20) {
                this.userHistory = this.userHistory.slice(0, 20);
            }
            
            this.saveUserHistory();
            this.recommendationCache.clear();
            
            console.log(`Added to history: ${postTitle}`);
        }
        
        trackInteraction(postId, type, metadata = {}) {
            // This is called when user interacts with a post
            const interaction = {
                postId,
                type,
                timestamp: Date.now(),
                metadata
            };
            
            // Store in localStorage for future reference
            const interactions = JSON.parse(localStorage.getItem('blog_interactions') || '[]');
            interactions.push(interaction);
            
            if (interactions.length > 100) {
                interactions.shift();
            }
            
            localStorage.setItem('blog_interactions', JSON.stringify(interactions));
        }
        
        extractPostFeatures() {
            const features = {};
            
            // Extract category
            const categoryEl = document.querySelector('.category, .post-category, [data-category], .badge');
            features.category = categoryEl ? categoryEl.textContent.trim().toLowerCase().replace(/\s+/g, '_') : 'general';
            
            // Extract tags
            features.tags = [];
            document.querySelectorAll('.tag, .post-tag, .badge:not(.category)').forEach(tag => {
                const tagText = tag.textContent.trim().toLowerCase().replace(/\s+/g, '_');
                if (tagText && !features.tags.includes(tagText)) {
                    features.tags.push(tagText);
                }
            });
            
            // Extract author
            const authorEl = document.querySelector('.author, .post-author, [data-author]');
            features.author = authorEl ? authorEl.textContent.trim().toLowerCase().replace(/\s+/g, '_') : 'unknown';
            
            // Estimate read time from content length
            const contentEl = document.querySelector('.post-content, .content, article');
            if (contentEl) {
                const wordCount = contentEl.textContent.split(/\s+/).length;
                features.read_time = Math.max(1, Math.ceil(wordCount / 200)); // 200 words per minute
            } else {
                features.read_time = 5;
            }
            
            return this.normalizeFeatures(features);
        }
        
        normalizeFeatures(features) {
            const normalized = {};
            
            // Normalize category
            if (features.category) {
                const hash = this.stringToHash(features.category);
                normalized.category = hash / 1000000000;
            }
            
            // Add tags as binary features
            if (features.tags && features.tags.length > 0) {
                features.tags.forEach(tag => {
                    normalized[`tag_${tag}`] = 1;
                });
            }
            
            // Normalize author
            if (features.author) {
                const authorHash = this.stringToHash(features.author);
                normalized.author = authorHash / 1000000000;
            }
            
            // Normalize read time (assume max 30 minutes)
            if (features.read_time) {
                normalized.read_time = Math.min(features.read_time / 30, 1);
            }
            
            return normalized;
        }
        
        stringToHash(str) {
            let hash = 0;
            for (let i = 0; i < str.length; i++) {
                hash = ((hash << 5) - hash) + str.charCodeAt(i);
                hash |= 0;
            }
            return Math.abs(hash);
        }
        
        calculateDistance(features1, features2) {
            if (this.distanceMetric === 'cosine') {
                return this.cosineDistance(features1, features2);
            }
            return this.cosineDistance(features1, features2);
        }
        
        cosineDistance(features1, features2) {
            const keys = new Set([...Object.keys(features1), ...Object.keys(features2)]);
            let dotProduct = 0;
            let norm1 = 0;
            let norm2 = 0;

            keys.forEach(key => {
                const val1 = features1[key] || 0;
                const val2 = features2[key] || 0;
                dotProduct += val1 * val2;
                norm1 += val1 * val1;
                norm2 += val2 * val2;
            });

            const similarity = dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
            return isNaN(similarity) ? 1 : 1 - similarity;
        }
        
        async getRecommendations(limit = 5) {
            // If not enough history, show popular/fallback
            if (this.userHistory.length < 1) {
                return this.getFallbackRecommendations(limit);
            }
            
            // Calculate average features from history
            const avgFeatures = this.calculateAverageFeatures();
            
            // Get all items from localStorage or extract from page
            await this.loadPageItems();
            
            const allItems = Array.from(this.items.entries());
            const recommendations = [];
            
            // Calculate similarity for each item
            allItems.forEach(([itemId, itemData]) => {
                // Skip if already in history
                if (this.userHistory.some(h => h.id === itemId)) {
                    return;
                }
                
                const distance = this.calculateDistance(avgFeatures, itemData.features);
                const similarity = 1 - distance;
                
                if (similarity > 0.1) { // Low threshold to show more recommendations
                    recommendations.push({
                        id: itemId,
                        title: itemData.metadata?.title || 'Untitled Post',
                        url: itemData.metadata?.url || '#',
                        category: itemData.metadata?.category || 'General',
                        similarity: similarity,
                        isPersonalized: true,
                        features: itemData.features
                    });
                }
            });
            
            // Sort by similarity
            recommendations.sort((a, b) => b.similarity - a.similarity);
            
            if (recommendations.length === 0) {
                return this.getFallbackRecommendations(limit);
            }
            
            return recommendations.slice(0, limit);
        }
        
        calculateAverageFeatures() {
            if (this.userHistory.length === 0) {
                return {};
            }
            
            const featureSums = {};
            const counts = {};
            
            this.userHistory.forEach(historyItem => {
                const itemData = this.items.get(historyItem.id);
                if (itemData && itemData.features) {
                    const features = itemData.features;
                    Object.keys(features).forEach(key => {
                        featureSums[key] = (featureSums[key] || 0) + features[key];
                        counts[key] = (counts[key] || 0) + 1;
                    });
                }
            });
            
            const avgFeatures = {};
            Object.keys(featureSums).forEach(key => {
                avgFeatures[key] = featureSums[key] / counts[key];
            });
            
            return avgFeatures;
        }
        
        async loadPageItems() {
            // Try to extract posts from current page
            const postElements = document.querySelectorAll('.post-card, .card, article');
            
            postElements.forEach((element, index) => {
                const title = element.querySelector('h1, h2, h3, h4, h5, .post-title')?.textContent || `Post ${index + 1}`;
                const url = element.querySelector('a')?.href || '#';
                const category = element.querySelector('.category, .badge')?.textContent || 'General';
                const postId = element.dataset.postId || element.id || `post_${Date.now()}_${index}`;
                
                // Extract features from the post element
                const features = this.extractFeaturesFromElement(element);
                
                this.items.set(postId, {
                    features: this.normalizeFeatures(features),
                    metadata: {
                        title: title.trim(),
                        url: url,
                        category: category.trim(),
                        element: element
                    }
                });
            });
            
            // Also load from localStorage
            try {
                const stored = localStorage.getItem('blog_knn_items');
                if (stored) {
                    const items = JSON.parse(stored);
                    items.forEach(item => {
                        this.items.set(item.id, {
                            features: item.features,
                            metadata: item.metadata
                        });
                    });
                }
            } catch (error) {
                console.warn('Could not load stored items:', error);
            }
        }
        
        extractFeaturesFromElement(element) {
            const features = {};
            
            // Extract category
            const categoryEl = element.querySelector('.category, .badge');
            features.category = categoryEl ? categoryEl.textContent.trim().toLowerCase().replace(/\s+/g, '_') : 'general';
            
            // Extract tags
            features.tags = [];
            element.querySelectorAll('.tag, .badge:not(.category)').forEach(tag => {
                const tagText = tag.textContent.trim().toLowerCase().replace(/\s+/g, '_');
                if (tagText && !features.tags.includes(tagText)) {
                    features.tags.push(tagText);
                }
            });
            
            // Extract author if available
            const authorEl = element.querySelector('.author');
            features.author = authorEl ? authorEl.textContent.trim().toLowerCase().replace(/\s+/g, '_') : 'unknown';
            
            return features;
        }
        
        getFallbackRecommendations(limit) {
            // Show recently viewed or random items as fallback
            const fallback = [];
            
            // First, try recently viewed
            this.userHistory.slice(0, limit).forEach(item => {
                fallback.push({
                    id: item.id,
                    title: item.title || 'Recently Viewed',
                    url: item.url || '#',
                    category: item.category || 'General',
                    similarity: 0.7,
                    isPersonalized: false,
                    isFallback: true,
                    reason: 'Recently viewed'
                });
            });
            
            // Fill with some default suggestions if needed
            if (fallback.length < limit) {
                const defaultSuggestions = [
                    { title: 'Getting Started with Django', category: 'Django', reason: 'Popular post' },
                    { title: 'Python Best Practices', category: 'Python', reason: 'Trending now' },
                    { title: 'Web Development Tips', category: 'Web Dev', reason: 'Editor\'s pick' },
                    { title: 'JavaScript Fundamentals', category: 'JavaScript', reason: 'Beginner friendly' },
                    { title: 'Database Design Patterns', category: 'Database', reason: 'Must read' }
                ];
                
                defaultSuggestions.slice(0, limit - fallback.length).forEach(suggestion => {
                    fallback.push({
                        id: `default_${Date.now()}_${Math.random()}`,
                        title: suggestion.title,
                        url: '#',
                        category: suggestion.category,
                        similarity: 0.5,
                        isPersonalized: false,
                        isFallback: true,
                        reason: suggestion.reason
                    });
                });
            }
            
            return fallback.slice(0, limit);
        }
        
        async initialize() {
            if (this.initialized) return true;
            
            console.log('Initializing KNN Recommendations...');
            
            // Extract current page info
            const currentPostId = this.getCurrentPostId();
            const currentPostTitle = document.title.replace(' - BlogSphere', '').replace(' - Blog', '');
            const currentPostCategory = this.getCurrentPostCategory();
            const currentUrl = window.location.href;
            
            if (currentPostId && currentPostTitle) {
                const features = this.extractPostFeatures();
                const metadata = {
                    title: currentPostTitle,
                    category: currentPostCategory,
                    url: currentUrl,
                    timestamp: Date.now()
                };
                
                // Add current post to items
                this.items.set(currentPostId, { features, metadata });
                
                // Add to user history (if it's a post page)
                if (window.location.pathname.includes('/post/') || 
                    window.location.pathname.includes('/blog/')) {
                    this.addToHistory(currentPostId, currentPostTitle, currentPostCategory, currentUrl);
                }
            }
            
            // Load other items from page
            await this.loadPageItems();
            
            // Initialize recommendations display
            this.renderRecommendations();
            
            this.initialized = true;
            console.log('KNN Recommendations initialized with', this.items.size, 'items');
            
            return true;
        }
        
        getCurrentPostId() {
            // Try to get post ID from various sources
            const path = window.location.pathname;
            const slug = path.split('/').filter(Boolean).pop();
            
            if (slug && slug !== 'posts' && slug !== 'blog') {
                return slug;
            }
            
            // Try from meta tag
            const metaPostId = document.querySelector('meta[name="post-id"]')?.content;
            if (metaPostId) return metaPostId;
            
            // Try from data attribute
            const dataPostId = document.querySelector('article, .post-detail')?.dataset.postId;
            if (dataPostId) return dataPostId;
            
            // Generate from URL
            return `post_${slug || 'home'}_${Date.now()}`;
        }
        
        getCurrentPostCategory() {
            const categoryEl = document.querySelector('.category, .post-category, .badge.bg-primary');
            if (categoryEl) {
                return categoryEl.textContent.trim();
            }
            
            // Try to extract from breadcrumb
            const breadcrumb = document.querySelector('.breadcrumb .active');
            if (breadcrumb && !breadcrumb.textContent.includes('Home')) {
                return breadcrumb.textContent.trim();
            }
            
            return 'General';
        }
        
        async renderRecommendations() {
            const container = document.getElementById('recommendations-container');
            if (!container) {
                // Try to create container if it doesn't exist
                this.createRecommendationsContainer();
                return;
            }
            
            // Show loading state
            container.innerHTML = `
                <div class="recommendations-loading">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span class="ms-2">Loading recommendations...</span>
                </div>
            `;
            
            // Get recommendations
            const recommendations = await this.getRecommendations(5);
            
            // Render recommendations
            if (recommendations.length > 0) {
                const html = this.generateRecommendationsHTML(recommendations);
                container.innerHTML = html;
                
                // Add click handlers
                this.addRecommendationClickHandlers();
            } else {
                container.innerHTML = `
                    <div class="recommendations-empty">
                        <p class="text-muted mb-0">No recommendations yet. Browse more posts!</p>
                    </div>
                `;
            }
        }
        
        createRecommendationsContainer() {
            // Check if we should create recommendations section
            const sidebar = document.querySelector('.col-lg-3, aside, .sidebar');
            if (!sidebar) return;
            
            // Create container
            const container = document.createElement('div');
            container.id = 'recommendations-container';
            container.className = 'card mb-4';
            container.innerHTML = `
                <div class="card-header">
                    <h5 class="mb-0">
                        <i class="fas fa-star me-2"></i>Recommended For You
                    </h5>
                </div>
                <div class="card-body">
                    <div class="recommendations-loading">
                        <div class="spinner-border spinner-border-sm text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <span class="ms-2">Loading recommendations...</span>
                    </div>
                </div>
            `;
            
            // Insert into sidebar
            sidebar.insertBefore(container, sidebar.firstChild);
        }
        
        generateRecommendationsHTML(recommendations) {
            let html = `
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">
                        <i class="fas fa-star me-2"></i>Recommended For You
                    </h5>
                    <button class="btn btn-sm btn-outline-primary" onclick="window.blogRecommender.refreshRecommendations()">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                </div>
                <div class="card-body">
                    <div class="recommendations-list">
            `;
            
            recommendations.forEach((rec, index) => {
                const similarityPercent = Math.round(rec.similarity * 100);
                const badgeColor = rec.isPersonalized ? 'bg-primary' : 'bg-secondary';
                
                html += `
                    <div class="recommendation-item mb-3" data-post-id="${rec.id}">
                        <div class="d-flex align-items-start">
                            <div class="flex-shrink-0">
                                <span class="badge ${badgeColor} rounded-pill">${index + 1}</span>
                            </div>
                            <div class="flex-grow-1 ms-3">
                                <h6 class="mb-1">
                                    <a href="${rec.url}" class="text-decoration-none recommendation-link" 
                                       data-post-id="${rec.id}" 
                                       data-title="${rec.title}">
                                        ${rec.title}
                                    </a>
                                </h6>
                                <div class="d-flex justify-content-between align-items-center">
                                    <small class="text-muted">
                                        ${rec.category}
                                        ${rec.reason ? `• ${rec.reason}` : ''}
                                    </small>
                                    ${rec.isPersonalized ? `
                                    <small class="text-primary">
                                        <i class="fas fa-bolt"></i> ${similarityPercent}% match
                                    </small>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                        ${index < recommendations.length - 1 ? '<hr class="my-2">' : ''}
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
            
            return html;
        }
        
        addRecommendationClickHandlers() {
            document.querySelectorAll('.recommendation-link').forEach(link => {
                link.addEventListener('click', (e) => {
                    const postId = link.dataset.postId;
                    const title = link.dataset.title;
                    
                    // Track click for recommendations
                    this.trackInteraction(postId, 'click_from_recommendation', {
                        title: title,
                        source: 'knn_recommendations'
                    });
                    
                    console.log(`Clicked recommendation: ${title}`);
                    
                    // The link will naturally navigate, but we track it first
                });
            });
        }
        
        refreshRecommendations() {
            this.recommendationCache.clear();
            this.renderRecommendations();
        }
    }
    
    // Initialize KNN Recommender
    window.blogRecommender = new BlogKNNRecommender();
    
    // Start the recommender after a short delay
    setTimeout(() => {
        window.blogRecommender.initialize();
    }, 1000);
    
    // Refresh recommendations every 2 minutes
    setInterval(() => {
        if (window.blogRecommender.initialized) {
            window.blogRecommender.refreshRecommendations();
        }
    }, 120000);
    
    // ============================================
    // HELPER FUNCTIONS
    // ============================================
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Add CSS for dynamic elements
    const style = document.createElement('style');
    style.textContent = `
        .error { border-color: #ef4444 !important; }
        .liked { color: #ef4444; }
        .fade-out { opacity: 0; transition: opacity 0.3s; }
        
        /* Recommendations Styling */
        .recommendations-loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            color: #6c757d;
        }
        
        .recommendation-item {
            transition: transform 0.2s ease;
        }
        
        .recommendation-item:hover {
            transform: translateX(5px);
        }
        
        .recommendation-link {
            color: #212529;
            transition: color 0.2s ease;
        }
        
        .recommendation-link:hover {
            color: #0d6efd;
            text-decoration: underline !important;
        }
        
        .recommendations-empty {
            text-align: center;
            padding: 20px;
            color: #6c757d;
        }
    `;
    document.head.appendChild(style);
    
    // ============================================
    // TRACK PAGE INTERACTIONS FOR KNN
    // ============================================
    
    // Track time on page for KNN
    let pageStartTime = Date.now();
    window.addEventListener('beforeunload', () => {
        const timeSpent = Date.now() - pageStartTime;
        if (window.blogRecommender && timeSpent > 3000) { // Only track if > 3 seconds
            const postId = window.blogRecommender.getCurrentPostId();
            window.blogRecommender.trackInteraction(postId, 'view', {
                duration: timeSpent,
                url: window.location.href
            });
        }
    });
    
    // Track scroll depth
    let maxScroll = 0;
    window.addEventListener('scroll', () => {
        const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
        maxScroll = Math.max(maxScroll, scrollPercent);
        
        if (window.blogRecommender && [25, 50, 75, 90].includes(Math.floor(maxScroll / 25) * 25)) {
            const postId = window.blogRecommender.getCurrentPostId();
            window.blogRecommender.trackInteraction(postId, 'scroll', {
                depth: maxScroll
            });
        }
    });
    
    // Track clicks on post links
    document.addEventListener('click', (e) => {
        const postLink = e.target.closest('a[href*="/post/"], a[href*="/blog/"]');
        if (postLink && window.blogRecommender) {
            const href = postLink.getAttribute('href');
            const postId = href.split('/').filter(Boolean).pop();
            
            window.blogRecommender.trackInteraction(postId, 'click', {
                text: postLink.textContent,
                href: href
            });
        }
    });
    
    console.log('KNN Recommendations System Loaded!');
});