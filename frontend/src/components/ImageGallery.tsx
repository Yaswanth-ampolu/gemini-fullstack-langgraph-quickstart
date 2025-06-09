import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, ExternalLink, Eye, X } from 'lucide-react';

interface ImageData {
  url: string;
  title: string;
  source: string;
  alt: string;
}

interface ImageGalleryProps {
  images: ImageData[];
  searchQuery?: string;
}

export const ImageGallery: React.FC<ImageGalleryProps> = ({ images, searchQuery }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [loadingStates, setLoadingStates] = useState<{ [key: number]: boolean }>({});
  const [errorStates, setErrorStates] = useState<{ [key: number]: boolean }>({});
  const [validImages, setValidImages] = useState<ImageData[]>([]);

  // Filter out failed images and only show working ones
  useEffect(() => {
    const filterValidImages = () => {
      const valid = images.filter((_, index) => !errorStates[index]);
      setValidImages(valid);
    };
    filterValidImages();
  }, [images, errorStates]);

  if (!images || images.length === 0) {
    return null;
  }

  // Use validImages for display
  const displayImages = validImages.length > 0 ? validImages : images;
  const itemsPerView = 3;
  const maxIndex = Math.max(0, displayImages.length - itemsPerView);

  const goToPrevious = () => {
    setCurrentIndex(prev => Math.max(0, prev - 1));
  };

  const goToNext = () => {
    setCurrentIndex(prev => Math.min(maxIndex, prev + 1));
  };

  const openModal = (imageIndex: number) => {
    setSelectedImageIndex(imageIndex);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const goToPreviousModal = () => {
    setSelectedImageIndex(prev => prev > 0 ? prev - 1 : displayImages.length - 1);
  };

  const goToNextModal = () => {
    setSelectedImageIndex(prev => prev < displayImages.length - 1 ? prev + 1 : 0);
  };

  const handleImageLoad = (index: number) => {
    setLoadingStates(prev => ({ ...prev, [index]: false }));
  };

  const handleImageError = (index: number) => {
    setLoadingStates(prev => ({ ...prev, [index]: false }));
    setErrorStates(prev => ({ ...prev, [index]: true }));
  };

  const handleImageStart = (index: number) => {
    setLoadingStates(prev => ({ ...prev, [index]: true }));
    setErrorStates(prev => ({ ...prev, [index]: false }));
  };

  // Don't render if no valid images
  if (displayImages.length === 0) {
    return null;
  }

  return (
    <>
      <div className="bg-gray-900/60 rounded-xl p-4 border border-gray-600/30 mb-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-gray-200 flex items-center gap-2">
            🖼️ Related Images
            {searchQuery && (
              <span className="text-xs text-gray-400">for "{searchQuery}"</span>
            )}
          </h3>
          <div className="text-xs text-gray-400">
            {displayImages.length} image{displayImages.length !== 1 ? 's' : ''} found
          </div>
        </div>

        <div className="relative">
          {/* Main Gallery Container */}
          <div className="overflow-hidden rounded-lg">
            <div 
              className="flex transition-transform duration-300 ease-in-out gap-3"
              style={{ transform: `translateX(-${currentIndex * (100 / itemsPerView)}%)` }}
            >
              {displayImages.map((image, index) => {
                const originalIndex = images.findIndex(img => img.url === image.url);
                return (
                  <div 
                    key={index} 
                    className="flex-shrink-0 relative group cursor-pointer"
                    style={{ width: `${100 / itemsPerView}%` }}
                    onClick={() => openModal(index)}
                  >
                    <div className="aspect-square rounded-lg overflow-hidden bg-gradient-to-br from-blue-900/20 to-purple-900/20 border border-gray-600 hover:border-blue-500 transition-all duration-200 relative">
                      {/* Loading Skeleton */}
                      {loadingStates[originalIndex] && (
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/30 to-purple-900/30 animate-pulse flex items-center justify-center">
                          <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                        </div>
                      )}

                      {/* Actual Image */}
                      <img
                        src={image.url}
                        alt={image.alt}
                        title={image.title}
                        className={`w-full h-full object-cover group-hover:scale-105 transition-all duration-200 ${
                          loadingStates[originalIndex] ? 'opacity-0' : 'opacity-100'
                        }`}
                        onLoadStart={() => handleImageStart(originalIndex)}
                        onLoad={() => handleImageLoad(originalIndex)}
                        onError={() => handleImageError(originalIndex)}
                        loading="lazy"
                      />
                      
                      {/* Hover Overlay */}
                      {!loadingStates[originalIndex] && (
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity duration-200 flex items-center justify-center">
                          <Eye className="h-6 w-6 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                        </div>
                      )}
                    </div>
                    
                    {/* Image Info */}
                    {!loadingStates[originalIndex] && (
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2 rounded-b-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <p className="text-xs text-white font-medium truncate">
                          {image.title}
                        </p>
                        <p className="text-xs text-gray-300 truncate">
                          {image.source}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Navigation Arrows */}
          {displayImages.length > itemsPerView && (
            <>
              <button
                onClick={goToPrevious}
                disabled={currentIndex === 0}
                className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-3 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-full p-2 border border-gray-600 transition-all duration-200 z-10"
              >
                <ChevronLeft className="h-4 w-4 text-white" />
              </button>
              
              <button
                onClick={goToNext}
                disabled={currentIndex >= maxIndex}
                className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-3 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-full p-2 border border-gray-600 transition-all duration-200 z-10"
              >
                <ChevronRight className="h-4 w-4 text-white" />
              </button>
            </>
          )}

          {/* Dots Indicator */}
          {displayImages.length > itemsPerView && (
            <div className="flex justify-center mt-3 gap-1">
              {Array.from({ length: maxIndex + 1 }).map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentIndex(index)}
                  className={`w-2 h-2 rounded-full transition-all duration-200 ${
                    index === currentIndex 
                      ? 'bg-blue-500' 
                      : 'bg-gray-600 hover:bg-gray-500'
                  }`}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Compact Modal for Full Image View */}
      {isModalOpen && displayImages[selectedImageIndex] && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-90 p-4">
          <div className="relative max-w-5xl w-full max-h-[90vh] bg-gray-900 rounded-lg overflow-hidden border border-gray-700 flex flex-col">
            {/* Header with Close Button */}
            <div className="flex items-center justify-between p-4 bg-gray-800 border-b border-gray-700">
              <div className="flex items-center gap-3">
                <h3 className="text-lg font-medium text-white truncate">
                  {displayImages[selectedImageIndex].title}
                </h3>
                <span className="text-sm text-gray-400">
                  {selectedImageIndex + 1} of {displayImages.length}
                </span>
              </div>
              <button
                onClick={closeModal}
                className="bg-gray-700 hover:bg-gray-600 rounded-full p-2 transition-all duration-200"
              >
                <X className="h-5 w-5 text-white" />
              </button>
            </div>

            {/* Image Container with Navigation */}
            <div className="relative flex-1 bg-black flex items-center justify-center min-h-[400px]">
              {/* Previous Button */}
              {displayImages.length > 1 && (
                <button
                  onClick={goToPreviousModal}
                  className="absolute left-4 top-1/2 -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-70 rounded-full p-3 transition-all duration-200 z-10"
                >
                  <ChevronLeft className="h-6 w-6 text-white" />
                </button>
              )}

              {/* Image */}
              <img
                src={displayImages[selectedImageIndex].url}
                alt={displayImages[selectedImageIndex].alt}
                className="max-w-full max-h-full object-contain"
                style={{ maxHeight: 'calc(90vh - 140px)' }}
              />

              {/* Next Button */}
              {displayImages.length > 1 && (
                <button
                  onClick={goToNextModal}
                  className="absolute right-4 top-1/2 -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-70 rounded-full p-3 transition-all duration-200 z-10"
                >
                  <ChevronRight className="h-6 w-6 text-white" />
                </button>
              )}
            </div>

            {/* Footer with Image Info */}
            <div className="p-4 bg-gray-800 border-t border-gray-700">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-300">
                  Source: {displayImages[selectedImageIndex].source}
                </p>
                <a
                  href={displayImages[selectedImageIndex].url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-sm text-blue-400 hover:text-blue-300 transition-colors duration-200"
                >
                  <ExternalLink className="h-4 w-4" />
                  View Original
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}; 