import React, { useState } from 'react';
import { Search, ChevronDown } from 'lucide-react';
import { ScreeningFormData } from '../types';

const INDUSTRIES = [
  'SaaS','Fintech','Healthcare','Manufacturing',
  'Consumer','Energy','Real Estate','Technology','Retail','Other',
];

const SAMPLE: ScreeningFormData = {
  company_name: 'Acme Cloud Software',
  industry:     'SaaS',
  revenue:      '85000000',
  ebitda:       '22000000',
  growth_rate:  '28',
  debt:         '45000000',
  cash:         '12000000',
  country:      'United States',
};

interface Props {
  onSubmit: (data: ScreeningFormData) => void;
  loading:  boolean;
}

export const ScreeningForm: React.FC<Props> = ({ onSubmit, loading }) => {
  const [form, setForm] = useState<ScreeningFormData>(SAMPLE);

  const set = (k: keyof ScreeningFormData) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm(prev => ({ ...prev, [k]: e.target.value }));

  const handleSubmit = (e: React.FormEvent) => { e.preventDefault(); onSubmit(form); };

  const Field = ({
    label, name, type = 'text', placeholder, prefix,
  }: {
    label: string; name: keyof ScreeningFormData;
    type?: string; placeholder?: string; prefix?: string;
  }) => (
    <div className="flex flex-col gap-1.5">
      <label className="label">{label}</label>
      <div className="relative">
        {prefix && (
          <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 text-sm font-mono">
            {prefix}
          </span>
        )}
        <input
          className={`input ${prefix ? 'pl-7' : ''}`}
          type={type}
          value={form[name]}
          onChange={set(name)}
          placeholder={placeholder}
          required
        />
      </div>
    </div>
  );

  return (
    <form onSubmit={handleSubmit} className="card fade-in-up">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-base font-semibold text-slate-200">Deal Input</h2>
        <button
          type="button"
          className="text-xs text-brand-400 hover:text-brand-300 transition-colors"
          onClick={() => setForm(SAMPLE)}
        >
          Load Sample
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Field label="Company Name"   name="company_name" placeholder="Acme Corp" />

        <div className="flex flex-col gap-1.5">
          <label className="label">Industry</label>
          <div className="relative">
            <select className="input appearance-none pr-8" value={form.industry} onChange={set('industry')} required>
              {INDUSTRIES.map(i => <option key={i} value={i}>{i}</option>)}
            </select>
            <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
          </div>
        </div>

        <Field label="Revenue (USD)"    name="revenue"     prefix="$" placeholder="85000000" />
        <Field label="EBITDA (USD)"     name="ebitda"      prefix="$" placeholder="22000000" />
        <Field label="YoY Growth Rate" name="growth_rate" type="number" placeholder="28" />
        <Field label="Total Debt (USD)" name="debt"        prefix="$" placeholder="45000000" />
        <Field label="Cash (USD)"       name="cash"        prefix="$" placeholder="12000000" />
        <Field label="Country"          name="country"     placeholder="United States" />
      </div>

      <button type="submit" className="btn-primary mt-6 w-full justify-center" disabled={loading}>
        {loading ? (
          <><span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Screening…</>
        ) : (
          <><Search size={16} /> Screen Company</>
        )}
      </button>
    </form>
  );
};
