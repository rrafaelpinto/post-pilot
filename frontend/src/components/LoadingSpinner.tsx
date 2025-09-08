import React from 'react';
import { Spinner } from 'react-bootstrap';

interface LoadingSpinnerProps {
    size?: 'sm';
    text?: string;
    inline?: boolean;
    className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
    size,
    text = 'Loading...',
    inline = false,
    className = ''
}) => {
    if (inline) {
        return (
            <span className={`d-inline-flex align-items-center ${className}`}>
                <Spinner
                    animation="border"
                    size={size}
                    role="status"
                    className="me-2"
                />
                {text}
            </span>
        );
    }

    return (
        <div className={`d-flex flex-column align-items-center justify-content-center py-4 ${className}`}>
            <Spinner
                animation="border"
                size={size}
                role="status"
                className="mb-2"
            />
            <div>{text}</div>
        </div>
    );
};

export default LoadingSpinner;
