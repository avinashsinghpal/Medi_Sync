export default function LoadingSpinner({ size = 'md', fullScreen = false }) {
  const sizeMap = {
    sm: '1rem',
    md: '2rem',
    lg: '3rem',
  };

  const spinner = (
    <div
      style={{
        display: 'inline-block',
        width: sizeMap[size],
        height: sizeMap[size],
        border: '3px solid rgba(14, 165, 233, 0.2)',
        borderTopColor: '#0ea5e9', // var(--color-primary)
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
      }}
    />
  );

  if (fullScreen) {
    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: 'rgba(248, 250, 252, 0.8)', // var(--color-bg-primary) with opacity
          backdropFilter: 'blur(4px)',
          zIndex: 9999,
        }}
      >
        <style>
          {`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}
        </style>
        {spinner}
      </div>
    );
  }

  return (
    <>
      <style>
        {`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}
      </style>
      {spinner}
    </>
  );
}
