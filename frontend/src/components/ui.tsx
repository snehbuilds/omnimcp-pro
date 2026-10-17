import React, { createContext, useCallback, useContext, useEffect, useId, useRef, useState } from 'react';
import { CircleAlert, CircleCheck, Info, X } from 'lucide-react';
import { getPlatformMeta } from '../platforms';

export const PlatformGlyph: React.FC<{ id: string; size?: 'sm' | 'lg' }> = ({ id, size = 'sm' }) => {
  const meta = getPlatformMeta(id);
  return (
    <span
      aria-hidden="true"
      className={`platform-glyph ${size === 'lg' ? 'lg' : ''}`}
      style={{ '--glyph-bg': meta.bg, '--glyph-fg': meta.fg } as React.CSSProperties}
    >
      {meta.glyph}
    </span>
  );
};

interface PageHeaderProps {
  eyebrow?: React.ReactNode;
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ eyebrow, title, description, actions }) => (
  <header className="page-header">
    <div>
      {eyebrow && <div className="page-eyebrow">{eyebrow}</div>}
      <h1 className="page-title">{title}</h1>
      {description && <p className="page-description">{description}</p>}
    </div>
    {actions && <div className="page-actions">{actions}</div>}
  </header>
);

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: React.ReactNode;
  footer?: React.ReactNode;
  width?: number;
  children?: React.ReactNode;
  as?: 'div' | 'form';
  onSubmit?: (e: React.FormEvent) => void;
}

export const Modal: React.FC<ModalProps> = ({
  open,
  onClose,
  title,
  description,
  footer,
  width = 480,
  children,
  as = 'div',
  onSubmit,
}) => {
  const titleId = useId();
  const descId = useId();
  const dialogRef = useRef<HTMLDivElement & HTMLFormElement>(null);

  useEffect(() => {
    if (!open) return;
    const previouslyFocused = document.activeElement as HTMLElement | null;
    dialogRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = prevOverflow;
      previouslyFocused?.focus();
    };
  }, [open, onClose]);

  if (!open) return null;

  const Tag = as;

  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <Tag
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={description ? descId : undefined}
        tabIndex={-1}
        className="modal"
        style={{ '--modal-w': `${width}px` } as React.CSSProperties}
        onSubmit={onSubmit}
      >
        <div className="modal-header">
          <div>
            <h2 id={titleId} className="modal-title">
              {title}
            </h2>
            {description && (
              <div id={descId} className="modal-description">
                {description}
              </div>
            )}
          </div>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Close dialog">
            <X size={16} />
          </button>
        </div>
        {children && <div className="modal-body">{children}</div>}
        {footer && <div className="modal-footer">{footer}</div>}
      </Tag>
    </div>
  );
};

type ToastTone = 'ok' | 'error' | 'info';

interface ToastItem {
  id: number;
  tone: ToastTone;
  message: string;
}

const ToastContext = createContext<(message: string, tone?: ToastTone) => void>(() => {});

export const useToast = () => useContext(ToastContext);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const counter = useRef(0);

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const push = useCallback(
    (message: string, tone: ToastTone = 'info') => {
      const id = ++counter.current;
      setToasts((prev) => [...prev.slice(-2), { id, tone, message }]);
      window.setTimeout(() => dismiss(id), 4500);
    },
    [dismiss]
  );

  const iconFor = (tone: ToastTone) =>
    tone === 'ok' ? <CircleCheck size={16} /> : tone === 'error' ? <CircleAlert size={16} /> : <Info size={16} />;

  return (
    <ToastContext.Provider value={push}>
      {children}
      <div className="toast-region" role="status" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast-${t.tone}`}>
            {iconFor(t.tone)}
            <span style={{ flex: 1 }}>{t.message}</span>
            <button type="button" className="icon-btn" onClick={() => dismiss(t.id)} aria-label="Dismiss notification">
              <X size={14} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};
