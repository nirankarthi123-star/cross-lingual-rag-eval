import React, { useState, useEffect } from 'react';
import { getDashboardSummary, getDashboardResults } from '../services/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function DashboardPage() {
  // Summary & Stats State
  const [summary, setSummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [summaryError, setSummaryError] = useState('');

  // Results & Table State
  const [results, setResults] = useState([]);
  const [resultsLoading, setResultsLoading] = useState(true);
  const [resultsError, setResultsError] = useState('');

  // Filter Controls State
  const [filters, setFilters] = useState({
    language: '',
    mitigation: '',
    hallucination: '',
  });

  // Modal State
  const [selectedResult, setSelectedResult] = useState(null);

  // Load Summary
  const loadSummary = async () => {
    setSummaryLoading(true);
    setSummaryError('');
    try {
      const data = await getDashboardSummary();
      setSummary(data);
    } catch (err) {
      setSummaryError(err.message || 'Failed to load summary statistics.');
    } finally {
      setSummaryLoading(false);
    }
  };

  // Load Results
  const loadResults = async (currentFilters = filters) => {
    setResultsLoading(true);
    setResultsError('');
    try {
      const data = await getDashboardResults(currentFilters);
      setResults(data.results || []);
    } catch (err) {
      setResultsError(err.message || 'Failed to load experiment results.');
    } finally {
      setResultsLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
    loadResults(filters);
  }, []);

  // Filter Change Handler
  const handleFilterChange = (key, value) => {
    const updated = { ...filters, [key]: value };
    setFilters(updated);
    loadResults(updated);
  };

  const handleResetFilters = () => {
    const reset = { language: '', mitigation: '', hallucination: '' };
    setFilters(reset);
    loadResults(reset);
  };

  // Helper formatting functions
  const formatLang = (lang) => {
    if (lang === 'english') return 'English';
    if (lang === 'tamil_english') return 'Tamil-English';
    if (lang === 'hindi_english') return 'Hindi-English';
    return lang;
  };

  // Prepare Charts Data from Backend Condition Summaries
  const renderFaithfulnessChart = () => {
    if (!summary || !summary.condition_summaries) return null;
    const conds = summary.condition_summaries;

    const baseFaith = [
      conds.english_baseline?.mean || 0,
      conds.tamil_english_baseline?.mean || 0,
      conds.hindi_english_baseline?.mean || 0,
    ];

    const mitFaith = [
      conds.english_mitigated?.mean || 0,
      conds.tamil_english_mitigated?.mean || 0,
      conds.hindi_english_mitigated?.mean || 0,
    ];

    const data = {
      labels: ['English', 'Tamil-English', 'Hindi-English'],
      datasets: [
        {
          label: 'Baseline (No Normalization)',
          data: baseFaith,
          backgroundColor: 'rgba(120, 134, 146, 0.65)',
          borderColor: 'rgba(120, 134, 146, 1)',
          borderWidth: 1,
          borderRadius: 6,
        },
        {
          label: 'Mitigated (Normalized to English)',
          data: mitFaith,
          backgroundColor: 'rgba(191, 221, 242, 0.9)',
          borderColor: 'rgba(59, 114, 158, 1)',
          borderWidth: 1,
          borderRadius: 6,
        },
      ],
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          min: 0,
          max: 1,
          grid: { color: 'rgba(227, 231, 232, 0.6)' },
          ticks: { color: '#788692', font: { family: 'Plus Jakarta Sans', size: 11 } },
        },
        x: {
          grid: { display: false },
          ticks: { color: '#263746', font: { family: 'Plus Jakarta Sans', size: 12, weight: '500' } },
        },
      },
      plugins: {
        legend: {
          position: 'top',
          labels: { color: '#263746', font: { family: 'Plus Jakarta Sans', size: 12 } },
        },
      },
    };

    return <Bar data={data} options={options} />;
  };

  const renderHallucinationChart = () => {
    if (!summary || !summary.condition_summaries) return null;
    const conds = summary.condition_summaries;

    const baseHal = [
      (conds.english_baseline?.hallucination_rate || 0) * 100,
      (conds.tamil_english_baseline?.hallucination_rate || 0) * 100,
      (conds.hindi_english_baseline?.hallucination_rate || 0) * 100,
    ];

    const mitHal = [
      (conds.english_mitigated?.hallucination_rate || 0) * 100,
      (conds.tamil_english_mitigated?.hallucination_rate || 0) * 100,
      (conds.hindi_english_mitigated?.hallucination_rate || 0) * 100,
    ];

    const data = {
      labels: ['English', 'Tamil-English', 'Hindi-English'],
      datasets: [
        {
          label: 'Baseline Hallucination Rate (%)',
          data: baseHal,
          backgroundColor: 'rgba(214, 90, 90, 0.55)',
          borderColor: 'rgba(214, 90, 90, 1)',
          borderWidth: 1,
          borderRadius: 6,
        },
        {
          label: 'Mitigated Hallucination Rate (%)',
          data: mitHal,
          backgroundColor: 'rgba(67, 158, 103, 0.55)',
          borderColor: 'rgba(67, 158, 103, 1)',
          borderWidth: 1,
          borderRadius: 6,
        },
      ],
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          min: 0,
          max: 100,
          grid: { color: 'rgba(227, 231, 232, 0.6)' },
          ticks: { color: '#788692', font: { family: 'Plus Jakarta Sans', size: 11 }, callback: (v) => `${v}%` },
        },
        x: {
          grid: { display: false },
          ticks: { color: '#263746', font: { family: 'Plus Jakarta Sans', size: 12, weight: '500' } },
        },
      },
      plugins: {
        legend: {
          position: 'top',
          labels: { color: '#263746', font: { family: 'Plus Jakarta Sans', size: 12 } },
        },
      },
    };

    return <Bar data={data} options={options} />;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Overview Metrics Cards */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-dark-text)' }}>
            Evaluation Overview
          </h2>
          <button
            onClick={loadSummary}
            disabled={summaryLoading}
            className="btn btn-secondary"
            style={{ fontSize: '0.78rem', padding: '4px 10px' }}
          >
            {summaryLoading ? 'Refreshing…' : 'Refresh Overview'}
          </button>
        </div>

        {summaryLoading ? (
          <div className="card" style={{ fontSize: '0.85rem', color: 'var(--color-muted-text)' }}>
            Loading summary evaluation data…
          </div>
        ) : summaryError ? (
          <div className="card" style={{ fontSize: '0.85rem', color: 'var(--color-danger)', backgroundColor: '#FDF0F0', border: '1px solid #F5C6C6' }}>
            {summaryError}
          </div>
        ) : summary && summary.status === 'empty' ? (
          <div className="card" style={{ textAlign: 'center', padding: '32px 20px', color: 'var(--color-muted-text)' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-dark-text)', marginBottom: '6px' }}>
              No Experimental Results Available
            </h3>
            <p style={{ fontSize: '0.85rem' }}>
              Run the evaluation runner script (<code style={{ fontFamily: 'var(--font-mono)' }}>python scripts/run_experiment.py --all</code>) to populate Phase 10 benchmark data.
            </p>
          </div>
        ) : summary && summary.overview ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '14px' }}>
            <div style={{ backgroundColor: 'var(--color-cream)', padding: '16px', borderRadius: 'var(--radius-card)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Queries Evaluated</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--color-dark-text)', marginTop: '4px' }}>
                {summary.overview.total_queries_evaluated}
              </div>
            </div>

            <div style={{ backgroundColor: 'var(--color-cream)', padding: '16px', borderRadius: 'var(--radius-card)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Total Experiments</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--color-dark-text)', marginTop: '4px' }}>
                {summary.overview.total_experiments}
              </div>
            </div>

            <div style={{ backgroundColor: 'var(--color-cream)', padding: '16px', borderRadius: 'var(--radius-card)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Avg Faithfulness</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--color-dark-text)', marginTop: '4px' }}>
                {summary.overview.average_faithfulness !== undefined ? summary.overview.average_faithfulness.toFixed(3) : 'N/A'}
              </div>
            </div>

            <div style={{ backgroundColor: 'var(--color-cream)', padding: '16px', borderRadius: 'var(--radius-card)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-muted-text)', fontWeight: 500 }}>Hallucination Rate</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--color-dark-text)', marginTop: '4px' }}>
                {summary.overview.overall_hallucination_rate !== undefined
                  ? `${(summary.overview.overall_hallucination_rate * 100).toFixed(1)}%`
                  : 'N/A'}
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Fixed Success Criteria */}
      {summary && summary.success_criterion && summary.success_criterion.length > 0 && (
        <div>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-dark-text)', marginBottom: '4px' }}>
            Fixed Success Criteria
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--color-muted-text)', marginBottom: '12px' }}>
            Criterion: English baseline mean − mitigated code-mixed mean &le; 0.10
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
            {summary.success_criterion.map((c, i) => (
              <div key={i} className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <h3 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-dark-text)' }}>
                    {c.comparison ? c.comparison.replace(' versus ', ' vs ') : 'Comparison'}
                  </h3>
                  <span
                    className="badge"
                    style={{
                      backgroundColor: c.decision === 'MET' ? '#EEF8F2' : '#FDF0F0',
                      color: c.decision === 'MET' ? 'var(--color-success)' : 'var(--color-danger)',
                      border: `1px solid ${c.decision === 'MET' ? '#C8E8D5' : '#F5C6C6'}`,
                    }}
                  >
                    {c.decision}
                  </span>
                </div>

                <div style={{ fontSize: '0.82rem', color: 'var(--color-muted-text)', lineHeight: 1.6 }}>
                  <div>English Baseline Mean: <strong style={{ color: 'var(--color-dark-text)' }}>{c.english_baseline_mean ?? 'N/A'}</strong></div>
                  <div>Mitigated Mean: <strong style={{ color: 'var(--color-dark-text)' }}>{c.mitigated_mean ?? 'N/A'}</strong></div>
                  <div>Measured Difference: <strong style={{ color: 'var(--color-dark-text)' }}>{c.difference !== null ? c.difference : 'N/A'}</strong></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Visualizations Section */}
      {summary && summary.condition_summaries && (
        <div>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-dark-text)', marginBottom: '14px' }}>
            Condition Comparison Charts
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
            <div className="card" style={{ height: '300px' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-dark-text)', marginBottom: '10px' }}>
                Faithfulness Score by Condition
              </div>
              <div style={{ height: '230px' }}>
                {renderFaithfulnessChart()}
              </div>
            </div>

            <div className="card" style={{ height: '300px' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-dark-text)', marginBottom: '10px' }}>
                Hallucination Rate (%) by Condition
              </div>
              <div style={{ height: '230px' }}>
                {renderHallucinationChart()}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filterable Experiment Explorer Section */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <div>
            <h2 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-dark-text)' }}>
              Experiment Explorer
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--color-muted-text)', marginTop: '2px' }}>
              Filterable evaluation records from Phase 10 benchmark database.
            </p>
          </div>
          <button onClick={handleResetFilters} className="btn btn-secondary" style={{ fontSize: '0.78rem', padding: '4px 10px' }}>
            Reset Filters
          </button>
        </div>

        {/* Filter Controls Bar */}
        <div className="card" style={{ padding: '16px', marginBottom: '16px', display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center' }}>
          {/* Language Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--color-dark-text)' }}>Language:</label>
            <select
              value={filters.language}
              onChange={(e) => handleFilterChange('language', e.target.value)}
              style={{
                padding: '6px 10px',
                borderRadius: '8px',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-warm-cream)',
                fontSize: '0.82rem',
                color: 'var(--color-dark-text)',
                outline: 'none',
              }}
            >
              <option value="">All Languages</option>
              <option value="english">English</option>
              <option value="tamil_english">Tamil-English</option>
              <option value="hindi_english">Hindi-English</option>
            </select>
          </div>

          {/* Mitigation Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--color-dark-text)' }}>Mitigation:</label>
            <select
              value={filters.mitigation}
              onChange={(e) => handleFilterChange('mitigation', e.target.value)}
              style={{
                padding: '6px 10px',
                borderRadius: '8px',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-warm-cream)',
                fontSize: '0.82rem',
                color: 'var(--color-dark-text)',
                outline: 'none',
              }}
            >
              <option value="">All Conditions</option>
              <option value="true">Mitigated (ON)</option>
              <option value="false">Baseline (OFF)</option>
            </select>
          </div>

          {/* Hallucination Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--color-dark-text)' }}>Hallucination:</label>
            <select
              value={filters.hallucination}
              onChange={(e) => handleFilterChange('hallucination', e.target.value)}
              style={{
                padding: '6px 10px',
                borderRadius: '8px',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-warm-cream)',
                fontSize: '0.82rem',
                color: 'var(--color-dark-text)',
                outline: 'none',
              }}
            >
              <option value="">All Statuses</option>
              <option value="true">True (Failed)</option>
              <option value="false">False (Passed)</option>
            </select>
          </div>
        </div>

        {/* Experiment Results Table */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          {resultsLoading ? (
            <div style={{ padding: '24px', fontSize: '0.85rem', color: 'var(--color-muted-text)', textAlign: 'center' }}>
              Loading experiment results from backend…
            </div>
          ) : resultsError ? (
            <div style={{ padding: '24px', fontSize: '0.85rem', color: 'var(--color-danger)', textAlign: 'center' }}>
              {resultsError}
            </div>
          ) : results.length === 0 ? (
            <div style={{ padding: '32px 20px', fontSize: '0.85rem', color: 'var(--color-muted-text)', textAlign: 'center' }}>
              No experiments match the selected filters.
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
                <thead>
                  <tr style={{ backgroundColor: 'var(--color-warm-cream)', borderBottom: '1px solid var(--color-border)' }}>
                    <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-dark-text)' }}>QID</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-dark-text)' }}>Language</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-dark-text)' }}>Mitigation</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-dark-text)' }}>Faithfulness</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-dark-text)' }}>Hallucination</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-dark-text)' }}>Model</th>
                    <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-dark-text)' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r, idx) => (
                    <tr
                      key={r.id || idx}
                      style={{
                        borderBottom: idx === results.length - 1 ? 'none' : '1px solid var(--color-border)',
                        transition: 'background-color 0.15s ease',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-light-blue)')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      <td style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--color-dark-text)' }}>{r.question_id}</td>
                      <td style={{ padding: '12px 16px', color: 'var(--color-dark-text)' }}>{formatLang(r.language)}</td>
                      <td style={{ padding: '12px 16px' }}>
                        <span className="badge badge-soft">
                          {r.mitigation_enabled ? 'ON' : 'OFF'}
                        </span>
                      </td>
                      <td style={{ padding: '12px 16px', fontWeight: 600 }}>
                        {r.faithfulness_score !== undefined && r.faithfulness_score !== null ? Number(r.faithfulness_score).toFixed(3) : 'N/A'}
                      </td>
                      <td style={{ padding: '12px 16px' }}>
                        <span
                          className="badge"
                          style={{
                            backgroundColor: r.hallucination_flag ? '#FDF0F0' : '#EEF8F2',
                            color: r.hallucination_flag ? 'var(--color-danger)' : 'var(--color-success)',
                            border: `1px solid ${r.hallucination_flag ? '#F5C6C6' : '#C8E8D5'}`,
                          }}
                        >
                          {r.hallucination_flag ? 'TRUE' : 'FALSE'}
                        </span>
                      </td>
                      <td style={{ padding: '12px 16px', color: 'var(--color-muted-text)', fontSize: '0.8rem' }}>
                        {r.generator_model || 'Unknown'}
                      </td>
                      <td style={{ padding: '12px 16px' }}>
                        <button
                          onClick={() => setSelectedResult(r)}
                          className="btn btn-secondary"
                          style={{ fontSize: '0.75rem', padding: '4px 10px' }}
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Result Detail View Modal */}
      {selectedResult && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(38, 55, 70, 0.4)',
            backdropFilter: 'blur(2px)',
            display: 'flex',
            alignItems: 'center',
            justify: 'center',
            zIndex: 100,
            padding: '20px',
          }}
          onClick={() => setSelectedResult(null)}
        >
          <div
            className="panel"
            style={{
              maxWidth: '680px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              backgroundColor: 'var(--color-cream)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid var(--color-border)', paddingBottom: '12px' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--color-dark-text)' }}>
                Experiment Details: Question {selectedResult.question_id}
              </h3>
              <button
                onClick={() => setSelectedResult(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.2rem',
                  color: 'var(--color-muted-text)',
                  cursor: 'pointer',
                }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px', marginBottom: '20px' }}>
              <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--color-muted-text)' }}>Language</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{formatLang(selectedResult.language)}</div>
              </div>

              <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--color-muted-text)' }}>Mitigation</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{selectedResult.mitigation_enabled ? 'ON' : 'OFF'}</div>
              </div>

              <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--color-muted-text)' }}>Faithfulness</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>
                  {selectedResult.faithfulness_score !== undefined ? Number(selectedResult.faithfulness_score).toFixed(3) : 'N/A'}
                </div>
              </div>

              <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--color-muted-text)' }}>Hallucination</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: selectedResult.hallucination_flag ? 'var(--color-danger)' : 'var(--color-success)' }}>
                  {selectedResult.hallucination_flag ? 'TRUE' : 'FALSE'}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '0.85rem' }}>
              <div>
                <div style={{ fontWeight: 600, color: 'var(--color-muted-text)', marginBottom: '4px', fontSize: '0.75rem' }}>Original Query</div>
                <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                  {selectedResult.original_query}
                </div>
              </div>

              <div>
                <div style={{ fontWeight: 600, color: 'var(--color-muted-text)', marginBottom: '4px', fontSize: '0.75rem' }}>Normalized Query</div>
                <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
                  {selectedResult.normalized_query || '(None)'}
                </div>
              </div>

              <div>
                <div style={{ fontWeight: 600, color: 'var(--color-muted-text)', marginBottom: '4px', fontSize: '0.75rem' }}>Retrieved Context</div>
                <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-border)', whiteSpace: 'pre-wrap', maxHeight: '140px', overflowY: 'auto' }}>
                  {selectedResult.retrieved_context || '(None)'}
                </div>
              </div>

              <div>
                <div style={{ fontWeight: 600, color: 'var(--color-muted-text)', marginBottom: '4px', fontSize: '0.75rem' }}>Generated Answer</div>
                <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-border)', whiteSpace: 'pre-wrap' }}>
                  {selectedResult.generated_answer}
                </div>
              </div>

              <div>
                <div style={{ fontWeight: 600, color: 'var(--color-muted-text)', marginBottom: '4px', fontSize: '0.75rem' }}>Judge Explanation</div>
                <div style={{ backgroundColor: 'var(--color-warm-cream)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--color-border)', whiteSpace: 'pre-wrap' }}>
                  {selectedResult.judge_explanation || '(None)'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
