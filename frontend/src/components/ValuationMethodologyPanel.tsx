import React from 'react';
import { DealScreenResponse } from '../types';
import { fmt } from '../utils';

interface Props { result: DealScreenResponse; }

export const ValuationMethodologyPanel: React.FC<Props> = ({ result: r }) => {
  const v = r.valuation;

  const sections = [
    { title: 'Method Used', items: [v.method_used] },
    { title: 'Inputs Used', items: v.inputs_used },
    { title: 'Multiples Used', items: v.multiples_used },
    { title: 'Formulas Used', items: v.formulas_used },
    { title: 'Assumptions Used', items: v.assumptions_used },
  ];

  return (
    <div className="card fade-in-up space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-slate-200">Valuation Methodology</h2>
        <span className="text-sm font-mono tabular-nums text-brand-300">{fmt.usdM(v.enterprise_value)}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sections.map(section => (
          <div key={section.title} className="bg-surface-raised rounded-lg p-3">
            <p className="label mb-2">{section.title}</p>
            <ul className="space-y-1.5">
              {section.items.map((item, i) => (
                <li key={i} className="text-xs text-slate-400 leading-relaxed font-mono">{item}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};
