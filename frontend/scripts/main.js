// 初始化Vue应用
const app = new Vue({
    el: '#app',
    data: {
        // 当前页面
        currentPage: 'home',
        // API基础URL
        apiBaseUrl: 'http://localhost:5000/api',
        // 加载状态
        loading: {
            analysis: false,
            suggestion: false,
            problem: false,
            directQuestion: false
        },
        // 代码分析数据
        analysisData: {
            code: '',
            language: 'python',
            context: ''
        },
        // 代码建议数据
        suggestionData: {
            code: '',
            language: 'python',
            improvement_type: 'general'
        },
        // 问题解决数据
        problemData: {
            problem_description: '',
            code_context: '',
            language: 'python',
            use_qianwen: false
        },
        // 结果
        results: {
            analysis: null,
            suggestion: null,
            solution: null,
            directQuestion: null
        },
        // 直接提问数据
        directQuestionData: {
            question: ''
        },
        // 错误信息
        error: ''
    },
    methods: {
        // 分析代码
        analyzeCode() {
            if (!this.analysisData.code) {
                alert('请输入代码');
                return;
            }

            this.loading.analysis = true;
            this.error = '';
            this.results.analysis = null;

            axios.post(`${this.apiBaseUrl}/code-analysis/analyze`, this.analysisData)
                .then(response => {
                    this.results.analysis = response.data;
                })
                .catch(error => {
                    console.error('代码分析错误:', error);
                    this.error = error.response?.data?.error || '请求失败，请稍后再试';
                    alert(this.error);
                })
                .finally(() => {
                    this.loading.analysis = false;
                });
        },

        // 获取代码建议
        getSuggestions() {
            if (!this.suggestionData.code) {
                alert('请输入代码');
                return;
            }

            this.loading.suggestion = true;
            this.error = '';
            this.results.suggestion = null;

            axios.post(`${this.apiBaseUrl}/code-suggestion/suggest`, this.suggestionData)
                .then(response => {
                    this.results.suggestion = response.data;
                })
                .catch(error => {
                    console.error('获取代码建议错误:', error);
                    this.error = error.response?.data?.error || '请求失败，请稍后再试';
                    alert(this.error);
                })
                .finally(() => {
                    this.loading.suggestion = false;
                });
        },

        // 解决问题
        solveProblem() {
            if (!this.problemData.problem_description) {
                alert('请描述您的问题');
                return;
            }

            this.loading.problem = true;
            this.error = '';
            this.results.solution = null;

            axios.post(`${this.apiBaseUrl}/problem-solving/solve`, this.problemData)
                .then(response => {
                    this.results.solution = response.data;
                })
                .catch(error => {
                    console.error('解决问题错误:', error);
                    this.error = error.response?.data?.error || '请求失败，请稍后再试';
                    alert(this.error);
                })
                .finally(() => {
                    this.loading.problem = false;
                });
        },

        // 直接提问
        askDirectQuestion() {
            if (!this.directQuestionData.question) {
                alert('请输入您的问题');
                return;
            }

            this.loading.directQuestion = true;
            this.error = '';
            this.results.directQuestion = null;

            axios.post(`${this.apiBaseUrl}/direct-question/ask`, this.directQuestionData)
                .then(response => {
                    this.results.directQuestion = response.data;
                })
                .catch(error => {
                    console.error('提问错误:', error);
                    this.error = error.response?.data?.error || '请求失败，请稍后再试';
                    alert(this.error);
                })
                .finally(() => {
                    this.loading.directQuestion = false;
                });
        },

        // 清除表单
        clearForm(formType) {
            if (formType === 'analysis') {
                this.analysisData = {
                    code: '',
                    language: 'python',
                    context: ''
                };
                this.results.analysis = null;
            } else if (formType === 'suggestion') {
                this.suggestionData = {
                    code: '',
                    language: 'python',
                    improvement_type: 'general'
                };
                this.results.suggestion = null;
            } else if (formType === 'problem') {
                this.problemData = {
                    problem_description: '',
                    code_context: '',
                    language: 'python',
                    use_qianwen: false
                };
                this.results.solution = null;
            } else if (formType === 'directQuestion') {
                this.directQuestionData = {
                    question: ''
                };
                this.results.directQuestion = null;
            }
        }
    }
});