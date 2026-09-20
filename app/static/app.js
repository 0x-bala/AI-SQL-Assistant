document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const questionInput = document.getElementById('question-input');
    const btnAsk = document.getElementById('btn-ask');
    const btnClear = document.getElementById('btn-clear');
    const btnNewQuery = document.getElementById('btn-new-query');
    
    const loader = document.getElementById('loader');
    const progressStepText = document.getElementById('progress-step-text');
    
    const securityBar = document.getElementById('security-bar');
    const resultsSection = document.getElementById('results-section');
    
    const errorBanner = document.getElementById('error-banner');
    const errorTitle = document.getElementById('error-title');
    const errorMessage = document.getElementById('error-message');
    
    const sqlCode = document.getElementById('sql-code');
    const explanationText = document.getElementById('explanation-text');
    const tablesUsedTags = document.getElementById('tables-used-tags');
    const columnsReturnedTags = document.getElementById('columns-returned-tags');
    
    const statTimeMeta = document.getElementById('stat-time-meta');
    const statRows = document.getElementById('stat-rows');
    const statTime = document.getElementById('stat-time');
    
    const tableHead = document.getElementById('table-head');
    const tableBody = document.getElementById('table-body');
    const gridSearchInput = document.getElementById('grid-search-input');
    const btnExportCsv = document.getElementById('btn-export-csv');
    
    const btnCopySql = document.getElementById('btn-copy-sql');
    const btnEditSql = document.getElementById('btn-edit-sql');
    const btnRunSql = document.getElementById('btn-run-sql');
    const toastContainer = document.getElementById('toast-container');
    const toastMessage = document.getElementById('toast-message');

    let currentQueryResult = null;

    // 1. Sidebar Schema Tree Toggle
    document.querySelectorAll('.table-node').forEach(node => {
        const title = node.querySelector('.table-title');
        const list = node.querySelector('.column-list');
        title.addEventListener('click', (e) => {
            e.stopPropagation();
            node.classList.toggle('open');
            list.classList.toggle('hidden');
        });
    });

    // 2. Recent Queries Navigation
    document.querySelectorAll('#recent-queries-list .nav-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('#recent-queries-list .nav-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            const q = item.getAttribute('data-q');
            if (q) {
                questionInput.value = q;
                handleAskAI();
            }
        });
    });

    // 3. New Query Action
    btnNewQuery.addEventListener('click', () => {
        questionInput.value = '';
        questionInput.focus();
        resetResultsView();
    });

    // 4. Text Example Buttons
    document.querySelectorAll('.btn-text-example').forEach(btn => {
        btn.addEventListener('click', () => {
            const q = btn.getAttribute('data-q');
            if (q) {
                questionInput.value = q;
                handleAskAI();
            }
        });
    });

    // 5. Clear Button
    btnClear.addEventListener('click', () => {
        questionInput.value = '';
        resetResultsView();
    });

    // 6. Ask AI Submit Actions
    btnAsk.addEventListener('click', handleAskAI);
    questionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleAskAI();
        }
    });

    // 7. Accordion Toggle for Explanation Panel
    const toggleExplanation = document.getElementById('toggle-explanation');
    if (toggleExplanation) {
        toggleExplanation.addEventListener('click', () => {
            const panel = toggleExplanation.closest('.explanation-panel');
            panel.classList.toggle('collapsed');
        });
    }

    // Main Execution Flow
    async function handleAskAI() {
        const question = questionInput.value.trim();
        if (!question) return;

        resetResultsView();
        showProgressLoading();

        try {
            const resp = await fetch('/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });

            const data = await resp.json();

            if (!resp.ok) {
                let detail = data.detail;
                let msg = typeof detail === 'string' ? detail : (detail.message || 'An error occurred during query execution.');
                if (detail.generated_sql) {
                    msg += `\nAttempted Query: ${detail.generated_sql}`;
                }
                throw new Error(msg);
            }

            currentQueryResult = data;
            renderResults(data);
        } catch (err) {
            showSecurityAlert(err.message);
        } finally {
            loader.classList.add('hidden');
        }
    }

    function showProgressLoading() {
        loader.classList.remove('hidden');
        progressStepText.textContent = 'Analyzing PostgreSQL schema & parameters...';
        
        setTimeout(() => {
            if (!loader.classList.contains('hidden')) {
                progressStepText.textContent = 'Generating safe read-only SQL query...';
            }
        }, 300);

        setTimeout(() => {
            if (!loader.classList.contains('hidden')) {
                progressStepText.textContent = 'Running AST security validation & executing against database...';
            }
        }, 600);
    }

    function resetResultsView() {
        errorBanner.classList.add('hidden');
        securityBar.classList.add('hidden');
        resultsSection.classList.add('hidden');
        loader.classList.add('hidden');
        currentQueryResult = null;
    }

    function renderResults(data) {
        // SQL Output
        sqlCode.textContent = data.sql;
        explanationText.textContent = data.explanation;

        // Metrics
        statRows.textContent = `${data.row_count} rows`;
        statTime.textContent = `${data.execution_time_ms} ms`;
        statTimeMeta.textContent = `Execution time: ${data.execution_time_ms} ms`;

        // Render Tables Used Tags
        tablesUsedTags.innerHTML = '';
        if (data.tables_used && data.tables_used.length > 0) {
            data.tables_used.forEach(tbl => {
                const tag = document.createElement('span');
                tag.textContent = tbl;
                tablesUsedTags.appendChild(tag);
            });
        } else {
            tablesUsedTags.innerHTML = '<span style="color:#6E7681;">None</span>';
        }

        // Render Columns Tags
        columnsReturnedTags.innerHTML = '';
        if (data.columns && data.columns.length > 0) {
            data.columns.forEach(col => {
                const tag = document.createElement('span');
                tag.textContent = col;
                columnsReturnedTags.appendChild(tag);
            });
        }

        // Render Data Grid Header
        tableHead.innerHTML = '';
        const trHead = document.createElement('tr');
        data.columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col;
            trHead.appendChild(th);
        });
        tableHead.appendChild(trHead);

        // Render Data Grid Body
        renderTableRows(data.rows, data.columns);

        securityBar.classList.remove('hidden');
        resultsSection.classList.remove('hidden');
    }

    function renderTableRows(rows, columns) {
        tableBody.innerHTML = '';

        if (!rows || rows.length === 0) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = columns ? columns.length : 1;
            td.textContent = 'No matching records found.';
            td.style.textAlign = 'center';
            td.style.color = '#8B949E';
            td.style.padding = '20px';
            tr.appendChild(td);
            tableBody.appendChild(tr);
            return;
        }

        rows.forEach(row => {
            const tr = document.createElement('tr');
            row.forEach(val => {
                const td = document.createElement('td');
                if (val === null) {
                    td.textContent = 'NULL';
                    td.style.color = '#6E7681';
                    td.style.fontStyle = 'italic';
                } else {
                    td.textContent = val;
                }

                // Copy cell content on click
                td.addEventListener('click', (e) => {
                    e.stopPropagation();
                    navigator.clipboard.writeText(td.textContent);
                    showToast(`Copied cell: "${td.textContent}"`);
                });

                tr.appendChild(td);
            });
            tableBody.appendChild(tr);
        });
    }

    function showSecurityAlert(msg) {
        errorTitle.textContent = 'BLOCKED QUERY';
        errorMessage.textContent = msg;
        errorBanner.classList.remove('hidden');
    }

    // 8. Grid Search Filter
    gridSearchInput.addEventListener('input', (e) => {
        if (!currentQueryResult) return;
        const term = e.target.value.toLowerCase().trim();
        if (!term) {
            renderTableRows(currentQueryResult.rows, currentQueryResult.columns);
            return;
        }

        const filtered = currentQueryResult.rows.filter(row => {
            return row.some(val => val !== null && String(val).toLowerCase().includes(term));
        });

        renderTableRows(filtered, currentQueryResult.columns);
        statRows.textContent = `${filtered.length} of ${currentQueryResult.rows.length} rows`;
    });

    // 9. Export to CSV
    btnExportCsv.addEventListener('click', () => {
        if (!currentQueryResult || !currentQueryResult.rows) return;

        let csvContent = 'data:text/csv;charset=utf-8,';
        csvContent += currentQueryResult.columns.join(',') + '\n';

        currentQueryResult.rows.forEach(row => {
            const formattedRow = row.map(val => {
                if (val === null) return '""';
                let str = String(val).replace(/"/g, '""');
                return `"${str}"`;
            });
            csvContent += formattedRow.join(',') + '\n';
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', `query_results_${Date.now()}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        showToast('Exported results to CSV');
    });

    // 10. Actions: Copy, Edit, Run SQL
    btnCopySql.addEventListener('click', () => {
        navigator.clipboard.writeText(sqlCode.textContent);
        showToast('SQL query copied to clipboard');
    });

    btnEditSql.addEventListener('click', () => {
        questionInput.focus();
        showToast('Focus returned to Query Editor');
    });

    btnRunSql.addEventListener('click', () => {
        handleAskAI();
    });

    function showToast(msg) {
        toastMessage.textContent = msg;
        toastContainer.classList.remove('hidden');
        setTimeout(() => {
            toastContainer.classList.add('hidden');
        }, 2500);
    }
});
