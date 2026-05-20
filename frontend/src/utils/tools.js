const realEstateImageIds = [
    26, 28, 42, 48, 65, 70, 73, 77, 81, 96,
    100, 103, 116, 119, 123, 144, 157, 160, 164, 169,
    177, 187, 193, 201, 212, 221, 237, 248, 257, 267,
    276, 287, 292, 303, 312, 321, 335, 342, 357, 367
]

export const getHouseImage = (images, index = 0, houseId = 0) => {
    if (images && images.length > index && images[index]) {
        return images[index]
    }
    const randomId = getRealEstateImageId(houseId)
    return `https://picsum.photos/id/${randomId}/800/600`
}

export const getRandomImage = (width = 800, height = 600, houseId = 0) => {
    const randomId = houseId > 0 ? getRealEstateImageId(houseId) : realEstateImageIds[Math.floor(Math.random() * realEstateImageIds.length)]
    return `https://picsum.photos/id/${randomId}/${width}/${height}`
}

const getRealEstateImageId = (seed) => {
    if (!seed || seed <= 0) {
        return realEstateImageIds[Math.floor(Math.random() * realEstateImageIds.length)]
    }
    return realEstateImageIds[seed % realEstateImageIds.length]
}
