export default function Container({ children, className = "" }) {
  return (
    <div className={`mx-auto w-full max-w-none 2xl:max-w-[1600px] px-6 ${className}`}>
      {children}
    </div>
  );
}


