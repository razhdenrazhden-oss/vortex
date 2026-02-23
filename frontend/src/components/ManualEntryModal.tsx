import { useState } from 'react';

export default function ManualEntryModal({
  open,
  onClose,
  onSubmit
}: {
  open: boolean;
  onClose: () => void;
  onSubmit: (payload: { hr?: number; power?: number; lactate?: number }) => Promise<void>;
}) {
  const [hr, setHr] = useState('');
  const [power, setPower] = useState('');
  const [lactate, setLactate] = useState('');

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end bg-black/50 p-3">
      <div className="w-full rounded-2xl bg-slate-900 p-4">
        <h3 className="text-lg font-semibold">Manual input</h3>
        <div className="mt-3 space-y-2">
          <input value={hr} onChange={(e) => setHr(e.target.value)} placeholder="HR" className="w-full rounded bg-slate-800 p-2" />
          <input value={power} onChange={(e) => setPower(e.target.value)} placeholder="Power" className="w-full rounded bg-slate-800 p-2" />
          <input value={lactate} onChange={(e) => setLactate(e.target.value)} placeholder="Lactate" className="w-full rounded bg-slate-800 p-2" />
        </div>
        <div className="mt-3 flex gap-2">
          <button className="flex-1 rounded bg-slate-700 py-2" onClick={onClose}>Cancel</button>
          <button
            className="flex-1 rounded bg-blue-600 py-2"
            onClick={async () => {
              await onSubmit({
                hr: hr ? Number(hr) : undefined,
                power: power ? Number(power) : undefined,
                lactate: lactate ? Number(lactate) : undefined
              });
              onClose();
            }}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
