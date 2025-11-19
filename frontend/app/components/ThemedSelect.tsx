"use client";

import { useState, useRef, useEffect } from "react";
import styles from "./ThemedSelect.module.css";

interface Option {
  value: string;
  label: string;
}

interface ThemedSelectProps {
  id: string;
  value: string;
  onChange: (value: string) => void;
  options: Option[];
  placeholder?: string;
  disabled?: boolean;
}

export default function ThemedSelect({
  id,
  value,
  onChange,
  options,
  placeholder = "Select an option",
  disabled = false,
}: ThemedSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const selectRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const selectedOption = value ? options.find(opt => opt.value === value) : null;

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        selectRef.current &&
        !selectRef.current.contains(event.target as Node) &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setHighlightedIndex(-1);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen && dropdownRef.current && highlightedIndex >= 0) {
      const optionElement = dropdownRef.current.children[highlightedIndex] as HTMLElement;
      if (optionElement) {
        optionElement.scrollIntoView({ block: "nearest" });
      }
    }
  }, [highlightedIndex, isOpen]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return;

    switch (e.key) {
      case "Enter":
      case " ":
        e.preventDefault();
        if (isOpen && highlightedIndex >= 0) {
          onChange(options[highlightedIndex].value);
          setIsOpen(false);
          setHighlightedIndex(-1);
        } else {
          setIsOpen(true);
        }
        break;
      case "ArrowDown":
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setHighlightedIndex(prev =>
            prev < options.length - 1 ? prev + 1 : prev
          );
        }
        break;
      case "ArrowUp":
        e.preventDefault();
        if (isOpen) {
          setHighlightedIndex(prev => (prev > 0 ? prev - 1 : -1));
        }
        break;
      case "Escape":
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  const handleOptionClick = (optionValue: string) => {
    onChange(optionValue);
    setIsOpen(false);
    setHighlightedIndex(-1);
  };

  return (
    <div className={styles.selectContainer}>
      <div
        ref={selectRef}
        className={`${styles.selectTrigger} ${isOpen ? styles.selectTriggerOpen : ""} ${disabled ? styles.selectTriggerDisabled : ""}`}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        tabIndex={disabled ? -1 : 0}
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-controls={`${id}-dropdown`}
        aria-label={value ? selectedOption?.label : placeholder}
      >
        <span className={styles.selectValue}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <div className={styles.selectArrow}>
          <svg
            width="12"
            height="8"
            viewBox="0 0 12 8"
            fill="none"
            className={`${styles.arrowIcon} ${isOpen ? styles.arrowIconOpen : ""}`}
          >
            <path
              d="M1 1L6 6L11 1"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        <div className={styles.selectGlow}></div>
      </div>

      {isOpen && (
        <div
          ref={dropdownRef}
          id={`${id}-dropdown`}
          className={styles.dropdown}
          role="listbox"
        >
          <div className={styles.dropdownGlow}></div>
          {options.map((option, index) => {
            const isSelected = option.value === value;
            const isHighlighted = index === highlightedIndex;
            return (
              <div
                key={option.value}
                className={`${styles.option} ${isSelected ? styles.optionSelected : ""} ${isHighlighted ? styles.optionHighlighted : ""}`}
                onClick={() => handleOptionClick(option.value)}
                onMouseEnter={() => setHighlightedIndex(index)}
                role="option"
                aria-selected={isSelected}
              >
                <span className={styles.optionText}>{option.label}</span>
                {isSelected && (
                  <span className={styles.optionCheckmark}>✓</span>
                )}
                <div className={styles.optionGlow}></div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

